class FlyThingsError(Exception):
    """Base class for every error raised by the flythings library."""


class AuthenticationError(FlyThingsError):
    """Missing or rejected credentials (no token, failed login, HTTP 401/403)."""


class ApiError(FlyThingsError):
    """The server answered a request with an error status code."""

    def __init__(self, status_code: int, body: str, url: str) -> None:
        super().__init__(f"HTTP {status_code} from {url}: {body}")
        self.status_code = status_code
        self.body = body
        self.url = url


class NetworkError(FlyThingsError):
    """The server could not be reached: connection failure, timeout or another transport error."""


class SocketError(FlyThingsError):
    """A real-time or action socket could not be opened or used."""


class RateLimitError(FlyThingsError):
    """A real-time value was sent before the minimum interval elapsed."""
