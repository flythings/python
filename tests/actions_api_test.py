import json
import threading

import pytest
import requests

from flythings import ActionDataTypes, ActionsApi, FlyThings, FlyThingsError, SocketError, _sockets
from flythings.paths import ACTIONS_URL


def test_register_action_payload(client, session, sent_json):
    api = client.actions_api()
    options = [{"name": "A", "value": "a"}, {"name": "B", "value": "b"}]
    api.register_action(
        "reboot", lambda: 0, parameter_type="SELECTOR", alias="Reboot", action_options=options, json_template="{}"
    )
    assert session.request.call_args.args == ("POST", client.default.url + ACTIONS_URL)
    assert sent_json() == {
        "name": "reboot",
        "featureOfInterest": "device",
        "parameterType": "SELECTOR",
        "alias": "Reboot",
        "actionOptions": options,
        "jsonTemplate": "{}",
    }


def test_register_action_for_series_payload(client, session, sent_json):
    client.actions_api().register_action_for_series(
        "setpoint", "temperature", "C", lambda _value: 0, foi="other", parameter_type=ActionDataTypes.NUMBER
    )
    assert sent_json() == {
        "name": "setpoint",
        "featureOfInterest": "other",
        "parameterType": "NUMBER",
        "procedure": "sensor",
        "observableProperty": "temperature",
        "unit": "C",
    }


def test_register_action_for_series_without_unit(client, sent_json):
    client.actions_api().register_action_for_series("setpoint", "temperature", None, lambda: 0)
    assert "unit" not in sent_json()


def test_action_options_only_for_selector(client, session, sent_json):
    client.actions_api().register_action("a", lambda: 0, parameter_type="TEXT", action_options=["x"])
    assert "actionOptions" not in sent_json()


def test_register_errors(client, connection, session):
    api = client.actions_api()
    api.register_action("a", lambda: 0)
    with pytest.raises(ValueError, match="already registered"):
        api.register_action("a", lambda: 0)
    no_defaults = FlyThings(connection, session=session).actions_api()
    with pytest.raises(ValueError, match="device"):
        no_defaults.register_action("b", lambda: 0)
    with pytest.raises(ValueError, match="procedure"):
        no_defaults.register_action_for_series("b", "p", "u", lambda: 0, foi="d")
    with pytest.raises(ValueError, match="at least one"):
        no_defaults.start_listening("d")


@pytest.mark.parametrize(
    ("kind", "param", "expected"),
    [
        (ActionDataTypes.TEXT, "hi", "hi"),
        (ActionDataTypes.JSON, '{"a": 1}', '{"a": 1}'),
        (ActionDataTypes.JSON, {"a": 1}, {"a": 1}),  # not a string: passed as received, as in 2.x
        (ActionDataTypes.TEXT, 5, 5),
        (ActionDataTypes.ARRAY, "a;b", ["a", "b"]),
        (ActionDataTypes.BOOLEAN, "True", True),
        (ActionDataTypes.BOOLEAN, "no", False),
        (ActionDataTypes.NUMBER, "3.5", 3.5),
        (ActionDataTypes.NUMBER, "nope", None),
        (ActionDataTypes.BOOLEAN, 1, None),
        (ActionDataTypes.ARRAY, ["a"], None),
        (None, "x", None),
        (ActionDataTypes.TEXT, None, None),
    ],
)
def test_cast_parameter(kind, param, expected):
    assert ActionsApi._cast_parameter(param, kind) == expected


def message(name, action=None):
    body = {"timestamp": 5, "name": name, "actionLog": 9}
    if action is not None:
        body["action"] = action
    return json.dumps(body)


def test_handle_dispatches_by_arity(client, fake_socket):
    api = client.actions_api()
    seen = []
    api.register_action("zero", lambda: seen.append(()) or 0)
    api.register_action("one", lambda p: seen.append((p,)) or "done", parameter_type="NUMBER")
    api.register_action("two", lambda p, ts: seen.append((p, ts)))
    api.register_action("three", lambda p, ts, log: seen.append((p, ts, log)) or "multi\nline")

    def fails():
        msg = "boom"
        raise RuntimeError(msg)

    api.register_action("fails", fails)
    sock = fake_socket()

    api._handle(sock, "DEVICE", "dev")
    api._handle(sock, "@PING@", "dev")
    api._handle(sock, message("unknown"), "dev")
    for name in ("zero", "one", "two", "three", "fails"):
        api._handle(sock, message(name, "4"), "dev")

    assert seen == [(), (4,), (None, 5), (None, 5, 9)]
    assert sock.sent_lines() == ["dev\n", "0\n", "done\n", "\n", "multiline\n", "\n"]


def test_send_progress(client, fake_socket):
    api = client.actions_api()
    with pytest.raises(SocketError):
        api.send_progress("50%")
    api._socket = fake_socket()
    api.send_progress("50%")
    api.send_progress(0)
    assert api._socket.sent_lines() == ["50%\n", "0\n"]


def test_listen_runs_callbacks_and_stops_promptly(monkeypatch, client, fake_socket):
    done = threading.Event()
    sockets = [fake_socket([b"DEVICE", message("go", "x").encode()])]

    def open_tcp(client, connection, path, timeout):
        assert path == ACTIONS_URL
        return sockets.pop(0) if sockets else fake_socket([BlockingIOError()] * 1000)

    monkeypatch.setattr(_sockets, "open_tcp", open_tcp)
    api = client.actions_api()
    api.retry_interval = 0.01
    api.register_action("go", lambda p: done.set() or p, parameter_type="TEXT")

    api.start_listening()
    api.start_listening()  # already running: no second thread
    assert done.wait(5)
    thread = api._thread
    assert thread is not None
    assert not thread.daemon  # keeps the program running, as in 2.x
    client.close()
    assert thread is not None
    assert not thread.is_alive()
    assert api._socket is None


def test_listen_survives_unexpected_message(monkeypatch, client, fake_socket, caplog):
    done = threading.Event()
    # A JSON message that is not an object fails with TypeError; the listener reconnects and keeps going
    sockets = [fake_socket([b"123"]), fake_socket([message("go", "x").encode()])]

    def open_tcp(*args, **kwargs):
        return sockets.pop(0) if sockets else fake_socket([BlockingIOError()] * 1000)

    monkeypatch.setattr(_sockets, "open_tcp", open_tcp)
    api = client.actions_api()
    api.retry_interval = 0.01
    api.register_action("go", lambda p: done.set() or p, parameter_type="TEXT")
    api.start_listening()
    assert done.wait(5)
    api.close()
    assert "TypeError" in caplog.text


def test_listen_retries_when_socket_cannot_open(monkeypatch, client):
    attempts = threading.Event()

    def open_tcp(*args, **kwargs):
        attempts.set()
        msg = "down"
        raise SocketError(msg)

    monkeypatch.setattr(_sockets, "open_tcp", open_tcp)
    api = client.actions_api()
    api.retry_interval = 0.01
    api.register_action("go", lambda: 0)
    api.start_listening()
    assert attempts.wait(5)
    api.stop_listening(timeout=5)
    assert api._thread is None


def test_listen_retries_after_network_error(client, session):
    attempts = threading.Semaphore(0)

    def fail(*args, **kwargs):
        attempts.release()
        msg = "down"
        raise requests.ConnectionError(msg)

    api = client.actions_api()
    api.retry_interval = 0.01
    api.register_action("go", lambda: 0)
    session.request.side_effect = fail
    api.start_listening()
    assert attempts.acquire(timeout=5)
    assert attempts.acquire(timeout=5)  # the thread is still alive and retried
    thread = api._thread
    api.stop_listening(timeout=5)
    assert thread is not None
    assert not thread.is_alive()


def listening_api(monkeypatch, client, fake_socket, name, callback):
    """Actions API listening on a socket that delivers one `name` action, then sockets that never deliver."""
    sockets = [fake_socket([b"DEVICE", message(name).encode()])]

    def open_tcp(*args, **kwargs):
        return sockets.pop(0) if sockets else fake_socket([BlockingIOError()] * 1000)

    monkeypatch.setattr(_sockets, "open_tcp", open_tcp)
    api = client.actions_api()
    api.retry_interval = 0.01
    api.register_action(name, callback)
    api.start_listening()
    return api


def test_close_from_callback(monkeypatch, client, fake_socket, caplog):
    closed = threading.Event()

    def shutdown():
        client.close()
        closed.set()

    api = listening_api(monkeypatch, client, fake_socket, "shutdown", shutdown)
    assert closed.wait(5)
    thread = api._thread
    assert thread is not None
    thread.join(5)
    assert not thread.is_alive()
    assert "failed" not in caplog.text
    assert "Error closing" not in caplog.text


def test_restart_while_callback_still_runs(monkeypatch, client, fake_socket):
    entered, release = threading.Event(), threading.Event()
    api = listening_api(monkeypatch, client, fake_socket, "slow", lambda: entered.set() or release.wait(5))
    assert entered.wait(5)
    thread = api._thread
    assert thread is not None

    api.stop_listening(timeout=0.01)  # the callback is still running
    assert api._thread is thread
    with pytest.raises(FlyThingsError, match="still stopping"):
        api.start_listening()

    release.set()
    thread.join(5)
    api.start_listening()
    assert api._thread is not thread
    api.close()
    assert api._thread is None
