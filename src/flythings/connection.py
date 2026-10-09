from dataclasses import KW_ONLY, dataclass
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal, TypeAlias

import requests

from flythings.errors import AuthenticationError, NetworkError
from flythings.paths import HTTP_, HTTPS_, LOGIN_DEVICE_URL, LOGIN_USER_URL

if TYPE_CHECKING:
    from flythings.schemas import LoginResponse

LoginType = Literal["USER", "DEVICE"]

DEFAULT_TIMEOUT: float = 1000


class Secret:
    """A credential that `repr`, `str`, f-strings and logs show as `**********`. `get_secret_value()` returns it.

    It is also a dataclass field (`token: Secret = Secret()`, as in `Connection`): `__init__` takes a plain string or a
    `Secret` and stores a `Secret`, and the attribute is `None` when not given. Dataclasses have no converters; a
    descriptor field is their documented replacement, and type checkers take the `__init__` parameter type from
    `__set__`.
    """

    __slots__ = ("_name", "_value")

    def __init__(self, value: str = "") -> None:
        self._value = value

    def get_secret_value(self) -> str:
        return self._value

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, instance: object | None, owner: type | None = None) -> "Secret | None":
        if instance is None:  # dataclasses read the field's default this way
            return None
        return instance.__dict__[self._name]

    def __set__(self, instance: object, value: "Credential | None") -> None:
        instance.__dict__[self._name] = Secret(value) if isinstance(value, str) else value

    def __repr__(self) -> str:
        return "Secret('**********')"

    def __str__(self) -> str:
        return "**********"

    def __bool__(self) -> bool:
        return bool(self._value)

    def __eq__(self, other: object) -> bool:
        return self._value == other._value if isinstance(other, Secret) else NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


Credential: TypeAlias = str | Secret
"""A token, plain or wrapped in `Secret`."""


def normalize_url(url: str) -> str:
    """Strip spaces and the trailing `/`, and add `http://` when the URL has no scheme."""
    url = url.strip().removesuffix("/")
    if not url.startswith((HTTP_, HTTPS_)):
        url = HTTP_ + url
    return url


class Url:
    """Dataclass field holding a URL normalized with `normalize_url`. It has no default, so it is required."""

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, instance: object | None, owner: type | None = None) -> str:
        if instance is None:  # raising tells dataclasses the field has no default
            raise AttributeError(self._name)
        return instance.__dict__[self._name]

    def __set__(self, instance: object, value: str) -> None:
        instance.__dict__[self._name] = normalize_url(value)


@dataclass(frozen=True)
class Connection:
    """A FlyThings server plus the credentials used against it.

    Use `token` for a bearer (authorization) token, or `session_token` for the token returned by a login. Tokens are
    given as plain strings or `Secret`s and stored as `Secret`s, and the URL is normalized. Two connections are equal
    when URL and credentials are equal.
    """

    url: Url = Url()
    token: Secret = Secret()
    _: KW_ONLY
    session_token: Secret = Secret()
    workspace: str | int | None = None

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token or self.session_token)

    def headers(self) -> dict[str, str]:
        """HTTP headers that authenticate a request on this connection."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token.get_secret_value()}"
            headers["x-auth-token"] = "-"
        elif self.session_token:
            headers["x-auth-token"] = self.session_token.get_secret_value()
        if self.workspace is not None:
            headers["Workspace"] = str(self.workspace)  # 2.x took a number; requests rejects non-string headers
        return headers

    def socket_credential(self) -> str:
        """Credential sent when a TCP socket asks for `X-AUTH-TOKEN`."""
        if self.token:
            return f"Bearer {self.token.get_secret_value()}"
        if self.session_token:
            return self.session_token.get_secret_value()
        msg = f"No credentials for {self.url}"
        raise AuthenticationError(msg)

    @classmethod
    def login(
        cls,
        url: str,
        user: str,
        password: str,
        login_type: LoginType = "USER",
        *,
        workspace: str | int | None = None,
        session: requests.Session | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> "Connection":
        """Log in with user (or device) and password, and return a connection holding the session token as a `Secret`.

        `login_type` is case-insensitive.
        """
        url = normalize_url(url)
        is_device = login_type.upper() == "DEVICE"
        path = LOGIN_DEVICE_URL if is_device else LOGIN_USER_URL
        getter = session.get if session is not None else requests.get
        try:
            response = getter(url + path, auth=(user, password), timeout=timeout)
        except requests.RequestException as e:
            msg = f"Login request to {url} failed: {e}"
            raise NetworkError(msg) from e
        if response.status_code != HTTPStatus.OK:
            msg = f"Login failed for {user!r} on {url} (HTTP {response.status_code})"
            raise AuthenticationError(msg)
        body: LoginResponse = response.json()
        if not is_device and "workspace" in body:
            workspace = str(body["workspace"])
        return cls(url, session_token=body["token"], workspace=workspace)
