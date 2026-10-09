"""Opening the TCP/UDP sockets used by the real-time and actions APIs."""

import socket
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from flythings.connection import Connection
from flythings.errors import SocketError
from flythings.paths import SOCKET_URL

if TYPE_CHECKING:
    from flythings.client import FlyThings

AUTH_REQUEST = "X-AUTH-TOKEN"
AUTH_ACCEPTED = "True"


def _endpoint(client: "FlyThings", connection: Connection, path: str) -> tuple[str, int]:
    """Host of the connection and the socket port the server publishes at `path`."""
    response = client.request("GET", path, connection=connection)
    host = urlparse(connection.url).hostname
    if host is None:
        msg = f"Cannot read a host name from {connection.url}"
        raise SocketError(msg)
    try:
        return host, int(response.text)
    except ValueError as e:
        msg = f"Invalid socket port from {connection.url}{path}: {response.text!r}"
        raise SocketError(msg) from e


def open_tcp(
    client: "FlyThings", connection: Connection, path: str = SOCKET_URL, timeout: float | None = 15.0
) -> socket.socket:
    """Connect and authenticate a TCP socket. Raises `SocketError` when the server refuses it."""
    credential = connection.socket_credential()
    address = _endpoint(client, connection, path)
    try:
        sock = socket.create_connection(address, timeout=timeout)
    except OSError as e:
        msg = f"Cannot connect to {address[0]}:{address[1]}"
        raise SocketError(msg) from e
    try:
        _authenticate(sock, credential)
    except OSError as e:
        sock.close()
        msg = f"Socket handshake with {address[0]}:{address[1]} failed"
        raise SocketError(msg) from e
    except SocketError:
        sock.close()
        raise
    return sock


def _authenticate(sock: socket.socket, credential: str) -> None:
    if sock.recv(1024).decode("utf-8") != AUTH_REQUEST:
        msg = "Socket unavailable: the server did not ask for credentials"
        raise SocketError(msg)
    sock.sendall((credential + "\n").encode("utf-8"))
    if sock.recv(4).decode("utf-8") != AUTH_ACCEPTED:
        msg = "Socket rejected the credentials"
        raise SocketError(msg)


def open_udp(client: "FlyThings", connection: Connection) -> socket.socket:
    address = _endpoint(client, connection, SOCKET_URL)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(address)
    except OSError as e:
        sock.close()
        msg = f"Cannot connect to {address[0]}:{address[1]}"
        raise SocketError(msg) from e
    return sock
