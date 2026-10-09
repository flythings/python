import json
import logging
from http import HTTPStatus
from pathlib import Path
from types import TracebackType
from typing import Protocol

import requests
from typing_extensions import Self

from flythings.apis.actions import ActionsApi
from flythings.apis.insertion import InsertionApi
from flythings.apis.query import QueryApi
from flythings.apis.realtime import RealTimeApi, WriteOptions
from flythings.apis.sos import SosApi
from flythings.apis.util import UtilApi
from flythings.connection import DEFAULT_TIMEOUT, Connection
from flythings.errors import ApiError, AuthenticationError, NetworkError
from flythings.series import Series

logger = logging.getLogger(__name__)

CONFIG_FILE = "Configuration.properties"
FOI_CACHE_FILE = ".foiCache"


class _Closeable(Protocol):
    def close(self) -> None: ...


def _close_or_log(api: _Closeable) -> None:
    try:
        api.close()
    except Exception:
        logger.exception("Error closing %r", api)


class FoiCache:
    """Remembers which devices were already registered on which server, so `register_device` posts each once.

    Kept in a tab-separated file in the 2.x format, `.foiCache` in the working directory by default. As in 2.x, the
    file is read on every check, so processes sharing it see each other's devices. Unlike 2.x, it is only created on
    the first write, never on import.
    """

    def __init__(self, path: str | Path = FOI_CACHE_FILE) -> None:
        self._path = Path(path)

    def contains(self, url: str, foi: str) -> bool:
        """Whether `(url, foi)` was already recorded."""
        return (url, foi) in self._entries()

    def add(self, url: str, foi: str) -> bool:
        """Record `(url, foi)`. Returns `False` when it was already known."""
        if self.contains(url, foi):
            return False
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(f"{url}\t{foi}\t\n")
        return True

    def _entries(self) -> set[tuple[str, str]]:
        if not self._path.exists():
            return set()
        entries: set[tuple[str, str]] = set()
        for line in self._path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:  # noqa: PLR2004
                entries.add((parts[0], parts[1]))
        return entries


class FlyThings:
    """Client for the FlyThings API.

    It holds one `Connection` and one HTTP session, and hands out the feature APIs (`insertion_api()`,
    `query_api()`, ...). To work with several servers or users, create one client per connection; a `session` passed in
    keeps cookies, so do not share one between clients with different credentials. Use it as a context manager, or call
    `close()`, so batched real-time values are flushed and listener threads and sockets are stopped.
    """

    def __init__(
        self,
        connection: Connection,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
        device: str | None = None,
        sensor: str | None = None,
        foi_cache: str | Path | FoiCache = FOI_CACHE_FILE,
    ) -> None:
        self.default = connection
        self.timeout = timeout
        self.device = device
        self.sensor = sensor
        self._owns_session = session is None
        self._session = session if session is not None else requests.Session()
        self.foi_cache = foi_cache if isinstance(foi_cache, FoiCache) else FoiCache(foi_cache)
        self._closeables: list[_Closeable] = []

    @classmethod
    def from_config_file(
        cls,
        path: str | Path = CONFIG_FILE,
        *,
        session: requests.Session | None = None,
        foi_cache: str | Path | FoiCache = FOI_CACHE_FILE,
    ) -> "FlyThings":
        """Build a client from a `key:value` properties file (see the README for the keys).

        Precedence for credentials: `user`/`password` login, then `authorization` (bearer), then `token`.
        """
        values = read_properties(path)
        url = values.get("server")
        if not url:
            msg = f"{path} has no server key"
            raise ValueError(msg)
        timeout = float(values["timeout"]) if values.get("timeout") else DEFAULT_TIMEOUT
        if values.get("user") and values.get("password"):
            login_type = "DEVICE" if values.get("login_type", "").upper() == "DEVICE" else "USER"
            connection = Connection.login(
                url, values["user"], values["password"], login_type, session=session, timeout=timeout
            )
        elif values.get("authorization"):
            connection = Connection(url, values["authorization"])
        else:
            connection = Connection(url, session_token=values.get("token") or None)
        return cls(
            connection,
            timeout=timeout,
            session=session,
            device=values.get("device") or None,
            sensor=values.get("sensor") or None,
            foi_cache=foi_cache,
        )

    def series(
        self,
        observable_property: str,
        foi: str | None = None,
        procedure: str | None = None,
        *,
        as_incremental: bool = False,
    ) -> Series:
        """Series using the client's default device and sensor unless given."""
        device, sensor = self.require_device(foi), self.require_sensor(procedure)
        return Series(device, sensor, observable_property, as_incremental=as_incremental)

    def require_device(self, foi: str | None = None) -> str:
        """`foi`, else the client's default device. Raises `ValueError` when there is neither."""
        device = foi or self.device
        if not device:
            msg = "A device (foi) is required when the client has no default device"
            raise ValueError(msg)
        return device

    def require_sensor(self, procedure: str | None = None) -> str:
        """`procedure`, else the client's default sensor. Raises `ValueError` when there is neither."""
        sensor = procedure or self.sensor
        if not sensor:
            msg = "A procedure (sensor) is required when the client has no default sensor"
            raise ValueError(msg)
        return sensor

    def request(
        self,
        method: str,
        path: str,
        *,
        connection: Connection | None = None,
        body: object = None,
        data: str | bytes | None = None,
    ) -> requests.Response:
        """Send an authenticated request to `path` on `connection` (default: this client's connection).

        `body` is serialized as JSON; `data` is sent as is. Raises `AuthenticationError` without credentials or on
        HTTP 401/403, `ApiError` on other HTTP errors, and `NetworkError` when the server cannot be reached.
        """
        route = connection or self.default
        if not route.is_authenticated:
            msg = f"No credentials for {route.url}"
            raise AuthenticationError(msg)
        url = route.url + path
        if body is not None:
            data = json.dumps(body)
        try:
            response = self._session.request(method, url, headers=route.headers(), data=data, timeout=self.timeout)
        except requests.RequestException as e:
            msg = f"{method} {url} failed: {e}"
            raise NetworkError(msg) from e
        if response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            msg = f"HTTP {response.status_code} from {url}"
            raise AuthenticationError(msg)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise ApiError(response.status_code, response.text, url)
        return response

    # API factories

    def insertion_api(self) -> InsertionApi:
        return InsertionApi(self, self.default)

    def query_api(self) -> QueryApi:
        return QueryApi(self, self.default)

    def realtime_api(self, write_options: WriteOptions | None = None) -> RealTimeApi:
        api = RealTimeApi(self, self.default, write_options)
        self._closeables.append(api)
        return api

    def actions_api(self, device: str | None = None) -> ActionsApi:
        api = ActionsApi(self, self.default, device or self.device)
        self._closeables.append(api)
        return api

    def sos_api(self) -> SosApi:
        return SosApi(self, self.default)

    def util_api(self) -> UtilApi:
        return UtilApi(self, self.default)

    # Lifecycle

    def close(self) -> None:
        """Close the APIs created by this client (flush batches, stop threads, close sockets), then the session."""
        closeables, self._closeables = self._closeables, []
        for api in closeables:
            _close_or_log(api)
        if self._owns_session:
            self._session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        self.close()


def read_properties(path: str | Path) -> dict[str, str]:
    """Read `key:value` lines. Keys are lower-cased; only the first `:` separates, so URLs keep their scheme."""
    values: dict[str, str] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip():
            values[key.strip().lower()] = value.strip()
    return values
