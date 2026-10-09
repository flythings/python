import json
import socket
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from flythings import Connection, FlyThings

URL = "https://api.example.test/api"
OTHER_URL = "https://other.example.test/api"


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    # No test may reach a real server: every way of opening a connection raises
    def refuse(*args, **kwargs):
        msg = "Tests must not open network connections"
        raise RuntimeError(msg)

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture(autouse=True)
def isolate_working_directory(monkeypatch, tmp_path):
    # Files written relative to the working directory, such as the default `.foiCache`, stay out of the repository
    monkeypatch.chdir(tmp_path)


def make_response(status_code: int = 200, body: Any = None, text: str | None = None) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    if text is None:
        text = "" if body is None else json.dumps(body)
    response.text = text
    response.content = text.encode("utf-8")
    if body is None:
        response.json.side_effect = ValueError("no JSON")
    else:
        response.json.return_value = body
    return response


@pytest.fixture
def respond() -> Callable[..., MagicMock]:
    return make_response


@pytest.fixture
def session() -> MagicMock:
    session = MagicMock(spec=requests.Session)
    session.request.return_value = make_response()
    return session


@pytest.fixture
def sent_json(session) -> Callable[[], Any]:
    """Decodes the JSON body of the last request sent through `session`."""
    return lambda: json.loads(session.request.call_args.kwargs["data"])


@pytest.fixture
def connection() -> Connection:
    return Connection(URL, "main-token")


@pytest.fixture
def other_connection() -> Connection:
    return Connection(OTHER_URL, "other-token")


@pytest.fixture
def client(connection, session) -> FlyThings:
    return FlyThings(connection, session=session, device="device", sensor="sensor")


class FakeSocket:
    """In-memory socket: `recv` pops scripted replies, `sendall` records what was sent."""

    def __init__(self, replies: list[bytes | BaseException] | None = None) -> None:
        self.replies = list(replies or [])
        self.sent: list[bytes] = []
        self.closed = False

    def recv(self, _size: int) -> bytes:
        if not self.replies:
            raise TimeoutError
        reply = self.replies.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        return reply

    def sendall(self, data: bytes) -> None:
        if self.closed:
            msg = "closed"
            raise OSError(msg)
        self.sent.append(data)

    def shutdown(self, _how: int) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def connect(self, _address: tuple[str, int]) -> None:
        pass

    def sent_lines(self) -> list[str]:
        return [chunk.decode("utf-8") for chunk in self.sent]


@pytest.fixture
def fake_socket() -> type[FakeSocket]:
    return FakeSocket
