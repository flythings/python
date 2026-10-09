import ast
import contextlib
import json
import logging
import socket
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from inspect import signature
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from flythings import _sockets
from flythings.connection import Connection
from flythings.errors import FlyThingsError, SocketError
from flythings.paths import ACTIONS_URL
from flythings.schemas import ActionOption, JsonValue

if TYPE_CHECKING:
    from flythings.client import FlyThings
    from flythings.schemas import ActionMessage, ActionRegistration

logger = logging.getLogger(__name__)

ActionCallback = Callable[..., Any]
"""Called with up to three arguments, by its arity: `()`, `(param)`, `(param, timestamp)` or
`(param, timestamp, action_log)`. Returning `0` or a string sends it back to the server as the result."""

PING_INTERVAL = 5.0
SOCKET_TIMEOUT = 60.0


class ActionDataTypes(Enum):
    BOOLEAN = "BOOLEAN"
    NUMBER = "NUMBER"
    TEXT = "TEXT"
    DATE = "DATE"
    SELECTOR = "SELECTOR"
    ARRAY = "ARRAY"
    JSON = "JSON"
    FILE = "FILE"
    LIVE = "LIVE"


_CONVERTERS: dict[ActionDataTypes, Callable[[Any], Any]] = {
    ActionDataTypes.BOOLEAN: lambda param: param.lower() == "true",
    ActionDataTypes.NUMBER: ast.literal_eval,
    ActionDataTypes.ARRAY: lambda param: param.split(";"),
}
"""How the parameter of a triggered action is converted before calling the callback; other types pass as received."""


@dataclass(frozen=True)
class _Registered:
    callback: ActionCallback
    parameter_type: ActionDataTypes | None
    arity: int


class ActionsApi:
    """Register actions for a device and run their callbacks when the platform triggers them.

    `start_listening()` runs a background thread holding the action socket. As in 2.x, it is not a daemon thread, so
    it keeps the program running until `stop_listening()` or `close()`.
    """

    def __init__(
        self, client: "FlyThings", connection: Connection, device: str | None = None, *, retry_interval: float = 30.0
    ) -> None:
        self._client = client
        self._connection = connection
        self.device = device
        self.retry_interval = retry_interval
        self._callbacks: dict[str, _Registered] = {}
        self._socket: socket.socket | None = None
        self._socket_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def register_action(
        self,
        name: str,
        callback: ActionCallback,
        foi: str | None = None,
        parameter_type: ActionDataTypes | str | None = None,
        alias: str | None = None,
        action_options: list[ActionOption] | None = None,
        json_template: str | None = None,
    ) -> None:
        """Register a device action on the server and the callback that runs it."""
        self._register(
            name,
            callback,
            foi,
            parameter_type,
            alias=alias,
            action_options=action_options,
            json_template=json_template,
        )

    def register_action_for_series(
        self,
        name: str,
        observable_property: str,
        unit: str | None,
        callback: ActionCallback,
        foi: str | None = None,
        procedure: str | None = None,
        parameter_type: ActionDataTypes | str | None = None,
        alias: str | None = None,
        action_options: list[ActionOption] | None = None,
        json_template: str | None = None,
    ) -> None:
        """Register an action attached to a series (the procedure defaults to the client's sensor)."""
        self._register(
            name,
            callback,
            foi,
            parameter_type,
            series=(self._client.require_sensor(procedure), observable_property, unit),
            alias=alias,
            action_options=action_options,
            json_template=json_template,
        )

    def start_listening(self, foi: str | None = None) -> None:
        """Open the action socket for the device in a background thread.

        As in 2.x, the thread is not a daemon: it keeps the program running until `stop_listening()` or `close()`.
        """
        device = self._device(foi)
        if not self._callbacks:
            msg = "Register at least one action before listening"
            raise ValueError(msg)
        if self._thread is not None and self._thread.is_alive():
            if not self._stop.is_set():
                return
            msg = "The previous listener is still stopping (an action callback is running); try again later"
            raise FlyThingsError(msg)
        self._stop.clear()
        self._thread = threading.Thread(target=self._listen, args=(device,), name="flythings-actions")
        self._thread.start()

    def stop_listening(self, timeout: float | None = None) -> None:
        """Stop the listener thread, waiting up to `timeout` seconds for a running callback to finish.

        Called from an action callback, it does not wait: the thread ends once the callback returns.
        """
        self._stop.set()
        self._reset_socket()
        thread = self._thread
        if thread is None or thread is threading.current_thread():
            return
        thread.join(timeout)
        if not thread.is_alive():
            self._thread = None

    def send_progress(self, message: str | int) -> None:
        """Report progress of the running action to the server."""
        with self._socket_lock:
            sock = self._socket
        if sock is None:
            msg = "The action socket is not open"
            raise SocketError(msg)
        _reply(sock, message)

    def close(self) -> None:
        self.stop_listening()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _device(self, foi: str | None) -> str:
        return self._client.require_device(foi or self.device)

    def _register(
        self,
        name: str,
        callback: ActionCallback,
        foi: str | None,
        parameter_type: ActionDataTypes | str | None,
        *,
        series: tuple[str, str, str | None] | None = None,
        alias: str | None,
        action_options: list[ActionOption] | None,
        json_template: str | None,
    ) -> None:
        if name in self._callbacks:
            msg = f"Action {name!r} is already registered"
            raise ValueError(msg)
        kind = ActionDataTypes(parameter_type) if parameter_type is not None else None
        body: ActionRegistration = {
            "name": name,
            "featureOfInterest": self._device(foi),
            "parameterType": kind.name if kind is not None else None,
        }
        if series is not None:
            body["procedure"], body["observableProperty"], unit = series
            if unit is not None:
                body["unit"] = unit
        if alias is not None:
            body["alias"] = alias
        if action_options is not None and kind is ActionDataTypes.SELECTOR:
            body["actionOptions"] = action_options
        if json_template is not None:
            body["jsonTemplate"] = json_template
        self._client.request("POST", ACTIONS_URL, connection=self._connection, body=body)
        self._callbacks[name] = _Registered(callback, kind, len(signature(callback).parameters))

    def _listen(self, device: str) -> None:
        last_ping = time.monotonic()
        while not self._stop.is_set():
            sock = self._current_socket()
            if sock is None:
                self._stop.wait(self.retry_interval)
                continue
            try:
                data = sock.recv(1024)
                if not data:
                    msg = "The server closed the action socket"
                    raise SocketError(msg)  # noqa: TRY301
                self._handle(sock, data.decode("utf-8"), device)
                if time.monotonic() - last_ping > PING_INTERVAL:
                    sock.sendall(b"Ping\n")
                    last_ping = time.monotonic()
            except (OSError, ValueError, KeyError, SocketError) as e:
                if self._stop.is_set():
                    break
                logger.warning("Action socket error (%s); reconnecting in %s s", e, self.retry_interval)
                self._reconnect_later()
            except Exception:  # an unexpected message must not end the listener, and every action with it
                if self._stop.is_set():
                    break
                logger.exception("Unexpected error on the action socket; reconnecting in %s s", self.retry_interval)
                self._reconnect_later()
        self._reset_socket()

    def _reconnect_later(self) -> None:
        self._reset_socket()
        self._stop.wait(self.retry_interval)

    def _current_socket(self) -> socket.socket | None:
        with self._socket_lock:
            if self._socket is None:
                try:
                    self._socket = _sockets.open_tcp(self._client, self._connection, ACTIONS_URL, SOCKET_TIMEOUT)
                except FlyThingsError as e:
                    logger.warning("Could not open the action socket (%s); retrying in %s s", e, self.retry_interval)
            return self._socket

    def _reset_socket(self) -> None:
        with self._socket_lock:
            sock, self._socket = self._socket, None
        if sock is not None:
            with contextlib.suppress(OSError):
                sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def _handle(self, sock: socket.socket, text: str, device: str) -> None:
        if text == "DEVICE":
            sock.sendall((device + "\n").encode("utf-8"))
            return
        if "@PING@" in text:
            return
        message: ActionMessage = json.loads(text)
        registered = self._callbacks.get(message["name"])
        if registered is None:
            return
        param = self._cast_parameter(message.get("action"), registered.parameter_type)
        args = (param, message["timestamp"], message["actionLog"])
        try:
            result = registered.callback(*args[: registered.arity])
        except Exception as e:
            logger.exception("Action %r failed", message["name"])
            result = e
        _reply(sock, result)

    @staticmethod
    def _cast_parameter(param: JsonValue, parameter_type: ActionDataTypes | None) -> Any:
        if param is None or parameter_type is None:
            return None
        converter = _CONVERTERS.get(parameter_type)
        if converter is None:
            return param
        try:
            return converter(param)
        except Exception:  # noqa: BLE001 (any parameter that cannot be converted is passed as None)
            return None


def _reply(sock: socket.socket, result: object) -> None:
    """Send a callback result: `0` and strings are sent as text, anything else as an empty line."""
    if result == 0 or isinstance(result, str):
        sock.sendall((str(result).replace("\n", "") + "\n").encode("utf-8"))
    else:
        sock.sendall(b"\n")
