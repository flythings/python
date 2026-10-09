from unittest.mock import MagicMock

import pytest
import requests

from flythings import ApiError, AuthenticationError, Connection, FlyThings, FoiCache, NetworkError, Secret, Series
from flythings.paths import LOGIN_DEVICE_URL


def test_request_sends_connection_headers_and_timeout(client, session):
    client.request("GET", "/x")
    session.request.assert_called_once_with(
        "GET", client.default.url + "/x", headers=client.default.headers(), data=None, timeout=1000
    )


def test_request_on_another_connection(client, session, other_connection):
    client.request("POST", "/x", connection=other_connection, body={"a": 1})
    assert session.request.call_args.kwargs["data"] == '{"a": 1}'
    assert session.request.call_args.args[1] == other_connection.url + "/x"
    assert session.request.call_args.kwargs["headers"]["Authorization"] == "Bearer other-token"


def test_request_without_credentials_raises(session):
    with pytest.raises(AuthenticationError):
        FlyThings(Connection("host"), session=session).request("GET", "/x")
    session.request.assert_not_called()


@pytest.mark.parametrize("status", [401, 403])
def test_request_auth_errors(client, session, respond, status):
    session.request.return_value = respond(status)
    with pytest.raises(AuthenticationError):
        client.request("GET", "/x")


def test_request_http_error(client, session, respond):
    session.request.return_value = respond(500, text="boom")
    with pytest.raises(ApiError) as excinfo:
        client.request("GET", "/x")
    assert excinfo.value.status_code == 500
    assert excinfo.value.body == "boom"


@pytest.mark.parametrize("error", [requests.ConnectionError("down"), requests.Timeout("slow")])
def test_request_network_error(client, session, error):
    session.request.side_effect = error
    with pytest.raises(NetworkError) as excinfo:
        client.request("GET", "/x")
    assert excinfo.value.__cause__ is error


def test_series_uses_default_device_and_sensor(client, session):
    assert client.series("temperature") == Series("device", "sensor", "temperature")
    assert client.series("p", "d2") == Series("d2", "sensor", "p")
    with pytest.raises(ValueError, match="device"):
        FlyThings(client.default, session=session).series("p")
    with pytest.raises(ValueError, match="sensor"):
        FlyThings(client.default, session=session, device="d").series("p")


def test_close_closes_owned_apis_but_not_injected_session(client, session):
    actions_api = client.actions_api()
    realtime_api = client.realtime_api()
    actions_api.close = MagicMock()
    realtime_api.close = MagicMock(side_effect=RuntimeError("ignored"))
    with client:
        pass
    actions_api.close.assert_called_once()
    realtime_api.close.assert_called_once()
    session.close.assert_not_called()


def test_close_closes_own_session(monkeypatch, connection):
    created = MagicMock()
    monkeypatch.setattr("flythings.client.requests.Session", lambda: created)
    FlyThings(connection).close()
    created.close.assert_called_once()


def test_foi_cache_defaults_to_2x_file(tmp_path, connection):
    assert not (tmp_path / ".foiCache").exists()  # not created on import or when the client is built
    cache = FlyThings(connection).foi_cache
    assert cache.add("u", "d")
    assert not cache.add("u", "d")
    assert cache.add("other", "d")
    assert (tmp_path / ".foiCache").read_text() == "u\td\t\nother\td\t\n"


def test_foi_cache_reads_file_on_every_check(tmp_path):
    path = tmp_path / "fois"
    cache = FoiCache(path)
    assert not cache.contains("u", "d")
    FoiCache(path).add("u", "d")  # another process sharing the file
    assert cache.contains("u", "d")


def test_foi_cache_file_is_lazy_and_persistent(tmp_path):
    path = tmp_path / "cache" / "fois"
    cache = FoiCache(path)
    assert not path.exists()
    assert cache.add("u", "d")
    assert path.read_text() == "u\td\t\n"
    assert not FoiCache(path).add("u", "d")
    assert FoiCache(path).contains("u", "d")
    assert not FoiCache(path).contains("u", "other")


def write_properties(tmp_path, text):
    path = tmp_path / "Configuration.properties"
    path.write_text(text)
    return path


def test_config_file_with_authorization(tmp_path, session):
    path = write_properties(
        tmp_path,
        "SERVER:https://api.example.test/api\nDEVICE:Python\nSENSOR:Client\nAUTHORIZATION: abc\nTOKEN: ignored\n"
        "TIMEOUT: 30\n",
    )
    client = FlyThings.from_config_file(path, session=session)
    assert client.default == Connection("https://api.example.test/api", "abc")
    assert (client.device, client.sensor, client.timeout) == ("Python", "Client", 30.0)


def test_config_file_with_session_token_and_defaults(tmp_path):
    client = FlyThings.from_config_file(write_properties(tmp_path, "server:https://h/api\ntoken: tkn\n"))
    assert client.default == Connection("https://h/api", session_token="tkn")
    assert isinstance(client.default.session_token, Secret)
    assert client.device is None


def test_config_file_requires_server(tmp_path):
    with pytest.raises(ValueError, match="no server"):
        FlyThings.from_config_file(write_properties(tmp_path, "token: tkn\n"))


def test_config_file_with_login(tmp_path, session, respond):
    session.get.return_value = respond(body={"token": "t0k"})
    path = write_properties(tmp_path, "server:host\nuser:me\npassword:pw\nlogin_type:device\n")
    client = FlyThings.from_config_file(path, session=session)
    assert session.get.call_args.args == ("http://host" + LOGIN_DEVICE_URL,)
    assert client.default == Connection("host", session_token="t0k")


def test_config_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        FlyThings.from_config_file(tmp_path / "missing.properties")
