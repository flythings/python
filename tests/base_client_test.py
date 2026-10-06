from unittest.mock import MagicMock

import pytest

from flythings import BaseClient, ServerConfig
from flythings.paths import LOGIN_DEVICE_URL, LOGIN_USER_URL


@pytest.mark.parametrize(
    ("server", "expected"),
    [
        ("beta.flythings.io/api", "http://beta.flythings.io/api"),
        ("  beta.flythings.io/api/ ", "http://beta.flythings.io/api"),
        ("https://beta.flythings.io/api", "https://beta.flythings.io/api"),
        ("http://localhost:8080", "http://localhost:8080"),
    ],
)
def test_set_server_normalizes_url(config, server, expected):
    client = BaseClient(config)
    assert client.set_server(server) == expected
    assert client.get_server() == expected


def test_set_server_none_keeps_current(config):
    client = BaseClient(config)
    assert client.set_server(None) == "http://beta.flythings.io/api"


def test_set_authorization_token_sets_bearer(config):
    client = BaseClient(config)
    assert client.set_authorization_token("abc") == "Bearer abc"
    assert client.get_headers()["x-auth-token"] == "-"


def test_token_from_config_wins_over_authorization_placeholder():
    client = BaseClient(ServerConfig(server="host", token="tkn"))
    assert client.get_headers()["x-auth-token"] == "tkn"


def test_setters_update_config(config):
    client = BaseClient(config)
    assert client.set_sensor("proc") == "proc"
    assert client.set_workspace("ws") == "ws"
    assert client.set_timeout(5) == 5
    assert client.set_custom_header("X-Test", "1") == "1"
    assert client.config.procedure == "proc"
    assert client.config.workspace == "ws"
    assert client.config.timeout == 5


def test_logout_clears_auth_headers(config):
    client = BaseClient(config)
    client.headers["Workspace"] = "ws"
    client.logout()
    assert client.get_headers()["x-auth-token"] == ""
    assert "Workspace" not in client.get_headers()
    assert "Authorization" not in client.get_headers()


@pytest.mark.parametrize(
    ("login_type", "url"),
    [("USER", LOGIN_USER_URL), ("DEVICE", LOGIN_DEVICE_URL), (None, LOGIN_USER_URL)],
)
def test_login_success_stores_token(monkeypatch, config, login_type, url):
    response = MagicMock(status_code=200, text='{"token": "t0k", "workspace": 7}')
    get = MagicMock(return_value=response)
    monkeypatch.setattr("flythings.base_client.requests.get", get)

    client = BaseClient(config)
    assert client.login("user", "secret", login_type) == "t0k"
    assert get.call_args.args[0] == "http://beta.flythings.io/api" + url
    assert client.get_headers()["x-auth-token"] == "t0k"


def test_login_failure_returns_none(monkeypatch, config):
    monkeypatch.setattr(
        "flythings.base_client.requests.get", MagicMock(return_value=MagicMock(status_code=401, text=""))
    )
    assert BaseClient(config).login("user", "wrong", "USER") is None


def test_load_data_by_file_reads_properties(tmp_path):
    properties = tmp_path / "Configuration.properties"
    properties.write_text("SERVER:beta.flythings.io/api\nDEVICE:Python\nSENSOR:Client\nTOKEN: abc\nTIMEOUT: 30\n")

    client = BaseClient(ServerConfig())
    client.load_data_by_file(str(properties))

    assert client.config.server == "beta.flythings.io/api"
    assert client.config.foi == "Python"
    assert client.config.procedure == "Client"
    assert client.config.timeout == "30"
    assert client.get_headers()["x-auth-token"] == "abc"


def test_load_data_by_file_missing_file_does_not_raise(tmp_path, capsys):
    BaseClient(ServerConfig()).load_data_by_file(str(tmp_path / "missing.properties"))
    assert "DONT EXIST" in capsys.readouterr().out
