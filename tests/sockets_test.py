import socket

import pytest

from flythings import Connection, FlyThings, SocketError, _sockets
from flythings.paths import ACTIONS_URL, SOCKET_URL


@pytest.fixture
def port_response(session, respond):
    session.request.return_value = respond(text="4321")


def patch_tcp(monkeypatch, sock):
    opened = {}

    def create_connection(address, timeout=None):
        opened.update(address=address, timeout=timeout)
        return sock

    monkeypatch.setattr(_sockets.socket, "create_connection", create_connection)
    return opened


def test_open_tcp_authenticates_with_bearer(monkeypatch, client, session, port_response, fake_socket):
    sock = fake_socket([b"X-AUTH-TOKEN", b"True"])
    opened = patch_tcp(monkeypatch, sock)

    assert _sockets.open_tcp(client, client.default, ACTIONS_URL, timeout=60) is sock
    assert session.request.call_args.args == ("GET", client.default.url + ACTIONS_URL)
    assert opened == {"address": ("api.example.test", 4321), "timeout": 60}
    assert sock.sent == [b"Bearer main-token\n"]


def test_open_tcp_session_token(monkeypatch, session, port_response, fake_socket):
    sock = fake_socket([b"X-AUTH-TOKEN", b"True"])
    patch_tcp(monkeypatch, sock)
    client = FlyThings(Connection("host", session_token="tkn"), session=session)
    _sockets.open_tcp(client, client.default)
    assert sock.sent == [b"tkn\n"]


@pytest.mark.parametrize("replies", [[b"NOPE"], [b"X-AUTH-TOKEN", b"Fals"], [OSError("reset")]])
def test_open_tcp_handshake_failures_close_socket(monkeypatch, client, port_response, fake_socket, replies):
    sock = fake_socket(replies)
    patch_tcp(monkeypatch, sock)
    with pytest.raises(SocketError):
        _sockets.open_tcp(client, client.default)
    assert sock.closed


def test_open_tcp_connection_refused(monkeypatch, client, port_response):
    def refuse(*args, **kwargs):
        raise ConnectionRefusedError

    monkeypatch.setattr(_sockets.socket, "create_connection", refuse)
    with pytest.raises(SocketError, match="Cannot connect"):
        _sockets.open_tcp(client, client.default)


def test_open_tcp_invalid_port(client, session, respond):
    session.request.return_value = respond(text="not-a-port")
    with pytest.raises(SocketError, match="Invalid socket port"):
        _sockets.open_tcp(client, client.default)


def test_open_udp_uses_host_name(monkeypatch, client, session, port_response, fake_socket):
    # 2.x split "http://host" on ":" and connected to "http"
    connected = []

    class Udp(fake_socket):
        def connect(self, address):
            connected.append(address)

    monkeypatch.setattr(_sockets.socket, "socket", lambda *args: Udp())
    _sockets.open_udp(client, client.default)
    assert connected == [("api.example.test", 4321)]
    assert session.request.call_args.args == ("GET", client.default.url + SOCKET_URL)


def test_open_udp_failure(monkeypatch, client, port_response, fake_socket):
    class Broken(fake_socket):
        def connect(self, address):
            raise OSError

    monkeypatch.setattr(_sockets.socket, "socket", lambda *args: Broken())
    with pytest.raises(SocketError):
        _sockets.open_udp(client, client.default)


def test_network_guard_blocks_real_sockets():
    with pytest.raises(RuntimeError, match="network"):
        socket.create_connection(("example.com", 80))
