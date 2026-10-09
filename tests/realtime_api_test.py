import json
import threading

import pytest
import requests

from flythings import ApiError, FlyThingsError, NetworkError, RateLimitError, SocketError, WriteOptions, _sockets


@pytest.fixture
def sockets(monkeypatch, fake_socket):
    opened = {"TCP": [], "UDP": []}

    def open_tcp(client, connection, *args, **kwargs):
        sock = fake_socket([b"ack"] * 10)
        opened["TCP"].append(sock)
        return sock

    def open_udp(client, connection):
        sock = fake_socket()
        opened["UDP"].append(sock)
        return sock

    monkeypatch.setattr(_sockets, "open_tcp", open_tcp)
    monkeypatch.setattr(_sockets, "open_udp", open_udp)
    return opened


@pytest.fixture
def clock(monkeypatch):
    now = {"ms": 1_000_000}
    monkeypatch.setattr("flythings.apis.realtime.now_millis", lambda: now["ms"])
    return now


def test_send_tcp_now(client, sockets, clock):
    api = client.realtime_api()
    api.send(7, 1.5, 100)
    (sock,) = sockets["TCP"]
    assert json.loads(sock.sent[0]) == {"seriesId": 7, "obs": [{"seriesId": 7, "timestamp": 100, "value": 1.5}]}
    assert sock.sent[0].endswith(b"\n")


def test_send_udp_includes_credential(client, sockets, clock):
    client.realtime_api().send(7, 1, 100, protocol="UDP")
    message = json.loads(sockets["UDP"][0].sent[0])
    assert message["X-AUTH-TOKEN"] == "Bearer main-token"
    assert message["data"]["seriesId"] == 7


@pytest.mark.parametrize(("protocol", "expected"), [("tcp", "TCP"), ("Udp", "UDP")])
def test_protocol_ignores_case(client, sockets, clock, protocol, expected):
    client.realtime_api().send(7, 1, 100, protocol=protocol)
    assert len(sockets[expected]) == 1


@pytest.mark.parametrize("protocol", ["HTTP", None])
def test_unknown_protocol(client, sockets, clock, protocol):
    with pytest.raises(ValueError, match="protocol"):
        client.realtime_api().send(7, 1, 100, protocol=protocol)
    assert sockets == {"TCP": [], "UDP": []}


def test_minimum_interval(client, sockets, clock):
    api = client.realtime_api()
    api.send(7, 1, 100)
    clock["ms"] += 1399
    with pytest.raises(RateLimitError):
        api.send(7, 2, 101)
    clock["ms"] += 1
    api.send(7, 3, 102)
    assert len(sockets["TCP"][0].sent) == 2


def test_socket_error_resets_socket(client, sockets, clock, fake_socket):
    api = client.realtime_api()
    api.send(7, 1, 100)
    sockets["TCP"][0].closed = True  # sendall now fails
    clock["ms"] += 2000
    with pytest.raises(SocketError):
        api.send(7, 2, 101)
    api.send(7, 2, 101)  # the failed send did not use up the rate-limit window
    assert len(sockets["TCP"]) == 2


def test_batch_queue_flush_and_close(client, sockets, clock):
    api = client.realtime_api(WriteOptions(batch=True, flush_interval=3600))
    start = clock["ms"]
    api.send(7, 2, start)
    clock["ms"] += 49
    with pytest.raises(RateLimitError):  # 49 ms after the timestamp of the last queued value
        api.send(7, 9, start + 49)
    clock["ms"] += 1
    api.send(7, 1, start - 100)
    api.send(8, 5, start)
    assert sockets["TCP"] == []

    api.flush()
    sent = [json.loads(line) for line in sockets["TCP"][0].sent]
    assert sent[0] == {
        "seriesId": 7,
        "obs": [
            {"seriesId": 7, "timestamp": start - 100, "value": 1},
            {"seriesId": 7, "timestamp": start, "value": 2},
        ],
    }
    assert sent[1]["seriesId"] == 8

    api.send(7, 3, clock["ms"])  # the queue was flushed, so nothing to wait for
    client.close()  # flushes the rest, stops the thread and closes the socket
    assert json.loads(sockets["TCP"][0].sent[-1])["obs"][0]["value"] == 3
    assert api._thread is not None
    assert not api._thread.is_alive()
    assert sockets["TCP"][0].closed
    with pytest.raises(FlyThingsError):
        api.send(7, 4, 400)
    api.close()  # idempotent


def test_batch_backfill(client, sockets, clock):
    # As in 2.x, the interval is measured from the timestamp of the last queued value, so past values queue at once
    api = client.realtime_api(WriteOptions(batch=True, flush_interval=3600))
    for i in range(5):
        api.send(7, i, 100 + i * 1000)
    assert len(api._pending[7]) == 5
    api.send(7, 9, clock["ms"])
    with pytest.raises(RateLimitError):  # the last value is now
        api.send(7, 10, 200)
    api._pending.clear()
    api.close()


def test_batch_flushed_at_exit(monkeypatch, client, sockets, clock):
    hooks = []
    monkeypatch.setattr("flythings.apis.realtime.atexit.register", hooks.append)
    monkeypatch.setattr("flythings.apis.realtime.atexit.unregister", hooks.remove)
    api = client.realtime_api(WriteOptions(batch=True, flush_interval=3600))
    api.send(7, 1, 100)
    (hook,) = hooks

    hook()  # what the interpreter does at exit when close() was never called
    assert json.loads(sockets["TCP"][0].sent[0])["obs"][0]["value"] == 1
    assert hooks == []  # close() removed the hook


def test_failed_flush_requeues(client, sockets, clock):
    api = client.realtime_api(WriteOptions(batch=True, flush_interval=3600))
    api.send(7, 1, 100)
    api.flush()
    sockets["TCP"][0].closed = True
    clock["ms"] += 100
    api.send(7, 2, 200)
    with pytest.raises(SocketError):
        api.flush()
    assert api._pending == {7: [{"seriesId": 7, "timestamp": 200, "value": 2}]}
    api.flush()  # a new socket is opened
    assert len(sockets["TCP"]) == 2
    api.close()


@pytest.mark.parametrize("error", [requests.ConnectionError("down"), None])
def test_failed_socket_open_requeues(client, session, respond, clock, error):
    # The socket port cannot be fetched: network failure, or an HTTP error from /socket
    if error is None:
        session.request.return_value = respond(502)
    else:
        session.request.side_effect = error
    api = client.realtime_api(WriteOptions(batch=True, flush_interval=3600))
    api.send(7, 1, 100)
    with pytest.raises(NetworkError if error is not None else ApiError):
        api.flush()
    assert api._pending == {7: [{"seriesId": 7, "timestamp": 100, "value": 1}]}


def test_batch_thread_survives_network_errors(client, session, clock):
    attempts = threading.Semaphore(0)

    def fail(*args, **kwargs):
        attempts.release()
        msg = "down"
        raise requests.ConnectionError(msg)

    session.request.side_effect = fail
    api = client.realtime_api(WriteOptions(batch=True, flush_interval=0.01))
    api.send(7, 1, 100)
    assert attempts.acquire(timeout=5)
    assert attempts.acquire(timeout=5)  # retried on the next interval
    assert api._thread is not None
    assert api._thread.is_alive()
    assert 7 in api._pending
    api._stop.set()
    api._thread.join(5)


def test_batch_thread_logs_failures(client, monkeypatch, caplog):
    api = client.realtime_api(WriteOptions(batch=True))

    def fail():
        msg = "down"
        raise SocketError(msg)

    monkeypatch.setattr(api, "flush", fail)
    api._flush_or_log()
    assert "not sent (down)" in caplog.text
