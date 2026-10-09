from dataclasses import FrozenInstanceError

import pytest
import requests

from flythings import AuthenticationError, Connection, NetworkError, Secret
from flythings.paths import LOGIN_DEVICE_URL, LOGIN_USER_URL


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("beta.flythings.io/api", "http://beta.flythings.io/api"),
        ("  beta.flythings.io/api/ ", "http://beta.flythings.io/api"),
        ("https://beta.flythings.io/api", "https://beta.flythings.io/api"),
        ("http://localhost:8080", "http://localhost:8080"),
    ],
)
def test_url_is_normalized(url, expected):
    assert Connection(url).url == expected


def test_bearer_token_headers():
    assert Connection("host", "abc").headers() == {
        "Content-Type": "application/json",
        "Authorization": "Bearer abc",
        "x-auth-token": "-",
    }


def test_session_token_headers_include_workspace():
    assert Connection("host", session_token="tkn", workspace="7").headers() == {
        "Content-Type": "application/json",
        "x-auth-token": "tkn",
        "Workspace": "7",
    }


def test_bearer_token_headers_include_workspace():
    assert Connection("host", "abc", workspace="7").headers()["Workspace"] == "7"


def test_numeric_workspace_is_sent_as_text(respond):
    # 2.x documented `set_workspace(Long)` and sent it as text; requests rejects a non-string header value
    session = requests.Session()
    session.get = lambda *args, **kwargs: respond(body={"token": "t0k"})
    connection = Connection.login("host", "dev", "secret", "DEVICE", workspace=5, session=session)
    assert connection == Connection("host", session_token="t0k", workspace=5)
    prepared = session.prepare_request(requests.Request("GET", connection.url, headers=connection.headers()))
    assert prepared.headers["Workspace"] == "5"


def test_no_credentials():
    connection = Connection("host")
    assert connection.headers() == {"Content-Type": "application/json"}
    assert not connection.is_authenticated
    with pytest.raises(AuthenticationError):
        connection.socket_credential()


def test_socket_credential():
    assert Connection("host", "abc").socket_credential() == "Bearer abc"
    assert Connection("host", session_token="tkn").socket_credential() == "tkn"


def test_equality_and_hash_use_url_and_credentials():
    assert Connection("host/", "a") == Connection("http://host", "a")
    assert Connection("host", "a") != Connection("host", "b")
    assert len({Connection("host", "a"), Connection("http://host/", "a"), Connection("host", "b")}) == 2


def test_connection_is_frozen():
    connection = Connection("host", "a")
    with pytest.raises(FrozenInstanceError):
        connection.url = "other"  # pyright: ignore[reportAttributeAccessIssue]


def test_tokens_are_hidden_from_repr():
    text = repr(Connection("host", "secret-bearer", session_token="secret-session"))
    assert "secret" not in text
    assert "http://host" in text


def test_secret_is_hidden_from_repr_str_and_format():
    secret = Secret("s3cr3t")
    assert "s3cr3t" not in f"{secret!r} {secret} {[secret]}"
    assert secret.get_secret_value() == "s3cr3t"


def test_secret_equality():
    assert Secret("a") == Secret("a")
    assert Secret("a") != Secret("b")
    assert Secret("a") != "a"
    assert not Secret("")


def test_tokens_are_stored_as_secrets():
    plain, wrapped = (
        Connection("host", "a", session_token="b"),
        Connection("host", Secret("a"), session_token=Secret("b")),
    )
    assert isinstance(plain.token, Secret)
    assert isinstance(plain.session_token, Secret)
    assert plain == wrapped
    assert len({plain, wrapped}) == 1
    assert Connection("host").token is None


def test_secret_credentials_are_sent_in_plain():
    bearer = Connection("host", Secret("abc"))
    assert bearer.headers()["Authorization"] == "Bearer abc"
    assert bearer.socket_credential() == "Bearer abc"
    session = Connection("host", session_token=Secret("tkn"))
    assert session.headers()["x-auth-token"] == "tkn"
    assert session.socket_credential() == "tkn"


@pytest.mark.parametrize(
    ("login_type", "path"),
    [("USER", LOGIN_USER_URL), ("DEVICE", LOGIN_DEVICE_URL), ("user", LOGIN_USER_URL), ("device", LOGIN_DEVICE_URL)],
)
def test_login_returns_new_connection(session, respond, login_type, path):
    session.get.return_value = respond(body={"token": "t0k", "workspace": 7})

    connection = Connection.login("host", "user", "secret", login_type, workspace="ws", session=session, timeout=5)

    assert session.get.call_args.args == ("http://host" + path,)
    assert session.get.call_args.kwargs == {"auth": ("user", "secret"), "timeout": 5}
    assert connection.session_token == Secret("t0k")
    # Only user logins take the workspace from the response
    assert connection.workspace == ("7" if login_type.upper() == "USER" else "ws")


def test_login_failure_raises(session, respond):
    session.get.return_value = respond(401)
    with pytest.raises(AuthenticationError):
        Connection.login("host", "user", "wrong", session=session)


def test_login_network_error_raises(session):
    session.get.side_effect = requests.ConnectionError("down")
    with pytest.raises(NetworkError):
        Connection.login("host", "user", "secret", session=session)
