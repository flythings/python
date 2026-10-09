import atexit
import json
import logging
import socket
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from typing_extensions import Self

from flythings import _sockets
from flythings._time import now_millis
from flythings.connection import Connection
from flythings.errors import FlyThingsError, RateLimitError, SocketError
from flythings.schemas import JsonValue, RealTimeMessage, RealTimePoint, UdpMessage

if TYPE_CHECKING:
    from flythings.client import FlyThings

logger = logging.getLogger(__name__)

SocketProtocol = Literal["TCP", "UDP"]


@dataclass(frozen=True)
class WriteOptions:
    """How `RealTimeApi` sends values.

    With `batch=True`, values are queued and a background thread sends them over TCP every `flush_interval` seconds.
    The minimum intervals are the platform's limits. Direct sends must be `realtime_min_interval_ms` apart. As in 2.x,
    a batched value is rejected when it is queued less than `batch_min_interval_ms` after the timestamp of the last
    value queued for its series, so values with past timestamps (a backfill) can be queued back to back.
    """

    batch: bool = False
    flush_interval: float = 5.0
    batch_min_interval_ms: int = 50
    realtime_min_interval_ms: int = 1400


class RealTimeApi:
    """Send values to series (by ID) through the real-time sockets."""

    def __init__(self, client: "FlyThings", connection: Connection, write_options: WriteOptions | None = None) -> None:
        self._client = client
        self._connection = connection
        self.write_options = write_options or WriteOptions()
        self._sockets: dict[SocketProtocol, socket.socket] = {}
        self._last_sent: int | None = None
        self._pending: dict[int, list[RealTimePoint]] = {}
        self._lock = threading.Lock()  # guards the queue
        self._io_lock = threading.Lock()  # guards the sockets
        self._stop = threading.Event()  # set by close()
        self._thread: threading.Thread | None = None

    def send(self, series_id: int, value: JsonValue, timestamp: int, protocol: SocketProtocol = "TCP") -> None:
        """Send a value now, or queue it when batching is enabled.

        `protocol` is `"TCP"` (the default) or `"UDP"`, case-insensitive; `None` is not accepted. Raises
        `RateLimitError` when called sooner than the minimum interval, and `SocketError` when the socket fails.
        """
        if self._stop.is_set():
            msg = "RealTimeApi is closed"
            raise FlyThingsError(msg)
        protocol = _protocol(protocol)
        point: RealTimePoint = {"seriesId": series_id, "timestamp": timestamp, "value": value}
        if self.write_options.batch:
            self._queue(point)
            return
        now = now_millis()
        if self._last_sent is not None and now - self._last_sent < self.write_options.realtime_min_interval_ms:
            msg = f"Real-time values must be at least {self.write_options.realtime_min_interval_ms} ms apart"
            raise RateLimitError(msg)
        self._send(protocol, {"seriesId": series_id, "obs": [point]})
        self._last_sent = now

    def flush(self) -> None:
        """Send the queued values now. If sending fails, the unsent values are queued again and the error is raised.

        A batch whose acknowledgement is lost is sent again, so the server may receive it twice.
        """
        with self._lock:
            pending, self._pending = self._pending, {}
        try:
            for series_id in list(pending):
                points = sorted(pending[series_id], key=lambda p: p["timestamp"])
                self._send("TCP", {"seriesId": series_id, "obs": points})
                del pending[series_id]
        except FlyThingsError:
            with self._lock:
                for series_id, points in pending.items():
                    self._pending[series_id] = points + self._pending.get(series_id, [])
            raise

    def close(self) -> None:
        """Stop the batch thread, send what is queued and close the sockets. Safe to call twice."""
        if self._stop.is_set():
            return
        self._stop.set()
        atexit.unregister(self._close_at_exit)
        if self._thread is not None:
            self._thread.join()
        try:
            if self._pending:
                self.flush()
        finally:
            for sock in self._sockets.values():
                sock.close()
            self._sockets.clear()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _queue(self, point: RealTimePoint) -> None:
        series_id = point["seriesId"]
        now = now_millis()
        with self._lock:
            queued = self._pending.get(series_id)
            if queued and now - queued[-1]["timestamp"] < self.write_options.batch_min_interval_ms:
                msg = (
                    f"A batched value must be queued at least {self.write_options.batch_min_interval_ms} ms after the "
                    "timestamp of the previous one of its series"
                )
                raise RateLimitError(msg)
            self._pending.setdefault(series_id, []).append(point)
            if self._thread is None:
                self._thread = threading.Thread(target=self._run_batches, name="flythings-realtime", daemon=True)
                self._thread.start()
                # The thread is a daemon so it never keeps the program alive; this sends what it had not sent yet
                atexit.register(self._close_at_exit)

    def _close_at_exit(self) -> None:
        try:
            self.close()
        except Exception:
            logger.exception("Queued real-time values could not be sent at exit")

    def _run_batches(self) -> None:
        while not self._stop.wait(self.write_options.flush_interval):
            self._flush_or_log()

    def _flush_or_log(self) -> None:
        try:
            self.flush()
        except FlyThingsError as e:
            logger.warning("Real-time batch not sent (%s); retrying in %s s", e, self.write_options.flush_interval)

    def _socket(self, protocol: SocketProtocol) -> socket.socket:
        sock = self._sockets.get(protocol)
        if sock is None:
            if protocol == "TCP":
                sock = _sockets.open_tcp(self._client, self._connection)
            else:
                sock = _sockets.open_udp(self._client, self._connection)
            self._sockets[protocol] = sock
        return sock

    def _send(self, protocol: SocketProtocol, message: RealTimeMessage) -> None:
        """Write `message` as a JSON line over TCP, or as a datagram carrying the credential over UDP."""
        if protocol == "TCP":
            data = json.dumps(message) + "\n"
        else:
            udp: UdpMessage = {"X-AUTH-TOKEN": self._connection.socket_credential(), "data": message}
            data = json.dumps(udp)
        with self._io_lock:
            sock = self._socket(protocol)
            try:
                sock.sendall(data.encode("utf-8"))
                if protocol == "TCP":
                    try:
                        sock.recv(1024)
                    except TimeoutError:
                        logger.debug("No acknowledgement from the real-time socket")
            except OSError as e:
                sock.close()
                self._sockets.pop(protocol, None)
                msg = f"Real-time {protocol} socket failed"
                raise SocketError(msg) from e


def _protocol(value: str | None) -> SocketProtocol:
    """`value` as `"TCP"` or `"UDP"`, ignoring case as 2.x did. Raises `ValueError` otherwise, `None` included."""
    upper = value.upper() if value is not None else value
    if upper == "TCP":
        return "TCP"
    if upper == "UDP":
        return "UDP"
    msg = f"Unknown protocol {value!r}; use 'TCP' (the default, also when the argument is omitted) or 'UDP'"
    raise ValueError(msg)
