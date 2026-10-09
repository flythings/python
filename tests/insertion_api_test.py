import json

import pytest

from flythings import ApiError, Observation, Series
from flythings.paths import (
    DEVICE_TYPES_URL,
    FOI_URL,
    PUBLISH_MULTIPLE_URL,
    PUBLISH_PLAIN_CSV_URL,
    PUBLISH_PREDICTION_MULTIPLE_URL,
    PUBLISH_PREDICTION_SINGLE_URL,
    PUBLISH_RECORD_URL,
    PUBLISH_SINGLE_URL,
)

BULK = [
    ("send_observations", PUBLISH_MULTIPLE_URL, "observations"),
    ("send_predictions", PUBLISH_PREDICTION_MULTIPLE_URL, "predictions"),
]


def calls(session):
    return [(c.args[0], c.args[1], c.kwargs) for c in session.request.call_args_list]


@pytest.mark.parametrize(("method", "path", "key"), BULK)
def test_bulk_send_chunks(client, session, method, path, key):
    series = Series("d", "s", "p")
    observations = [Observation(series, i, i) for i in range(2500)]

    getattr(client.insertion_api(), method)(observations)

    sent = calls(session)
    assert [(m, url) for m, url, _ in sent] == [("PUT", client.default.url + path)] * 3
    assert [len(json.loads(kw["data"])[key]) for _, _, kw in sent] == [1000, 1000, 500]
    assert json.loads(sent[0][2]["data"])[key][0] == {
        "observableProperty": "p",
        "procedure": "s",
        "foi": "d",
        "value": 0,
        "time": 0,
    }
    assert sent[0][2]["headers"]["Authorization"] == "Bearer main-token"


@pytest.mark.parametrize(("method", "path", "key"), BULK)
def test_bulk_send_accepts_payload_dicts(client, session, method, path, key, sent_json):
    payload = {"observableProperty": "p", "procedure": "s", "foi": "d", "value": 1}
    getattr(client.insertion_api(), method)([payload])
    assert [(m, url) for m, url, _ in calls(session)] == [("PUT", client.default.url + path)]
    assert sent_json() == {key: [payload]}


def test_bulk_send_empty_sends_nothing(client, session):
    client.insertion_api().send_observations([])
    session.request.assert_not_called()


@pytest.mark.parametrize(
    ("method", "path"), [("send_observation", PUBLISH_SINGLE_URL), ("send_prediction", PUBLISH_PREDICTION_SINGLE_URL)]
)
def test_single_send(client, session, method, path, sent_json):
    observation = Observation(Series("d", "s", "p"), 3)
    getattr(client.insertion_api(), method)(observation)
    assert session.request.call_args.args == ("PUT", client.default.url + path)
    assert sent_json() == observation.to_payload()


def test_send_record(client, session, respond, sent_json):
    session.request.return_value = respond(body={"ok": True})
    api = client.insertion_api()
    assert api.send_record(7, [1, 2]) == {"ok": True}
    assert session.request.call_args.args == ("PUT", f"{client.default.url}{PUBLISH_RECORD_URL}/7")
    assert sent_json() == [1, 2]
    api.send_record(7, "raw")
    assert session.request.call_args.kwargs["data"] == "raw"


def test_send_observations_csv_joins_lines(client, session):
    client.insertion_api().send_observations_csv(["a;1", "b;2"])
    assert session.request.call_args.args == ("POST", client.default.url + PUBLISH_PLAIN_CSV_URL)
    assert session.request.call_args.kwargs["data"] == "a;1\nb;2"


CSV = "123;1700000000000;20\n124;1700000000000;21\n"


def test_send_observations_csv_strips_line_endings(client, session):
    client.insertion_api().send_observations_csv(["a;1\n", "b;2\r\n"])
    assert session.request.call_args.kwargs["data"] == "a;1\nb;2"


@pytest.mark.parametrize("mode", ["r", "rb"])
def test_send_observations_csv_sends_files_as_is(client, session, tmp_path, mode):
    # As in 2.x, a file is sent unchanged: iterating it would double every line ending
    path = tmp_path / "obs.csv"
    path.write_text(CSV)
    with path.open(mode) as f:
        client.insertion_api().send_observations_csv(f)
    assert session.request.call_args.kwargs["data"] == (CSV if mode == "r" else CSV.encode())


def test_send_observations_csv_sends_bytes_as_is(client, session):
    client.insertion_api().send_observations_csv(CSV.encode())
    assert session.request.call_args.kwargs["data"] == CSV.encode()


def test_register_device_once_and_checks_type(client, session, respond):
    session.request.side_effect = [respond(body=["CUSTOM"]), respond()]
    api = client.insertion_api()
    geom = {"type": "Point", "coordinates": [1, 2]}

    assert api.register_device("dev", device_type="CUSTOM", geom=geom)
    assert not api.register_device("dev")
    assert api.register_device("dev", device_type="CUSTOM", always_update=False) is False

    first_get, first_post = session.request.call_args_list[:2]
    assert first_get.args == ("GET", client.default.url + DEVICE_TYPES_URL)
    assert first_post.args == ("POST", client.default.url + FOI_URL)
    assert json.loads(first_post.kwargs["data"]) == {
        "featureOfInterest": {"name": "dev", "geom": geom},
        "device": "CUSTOM",
    }


def test_failed_register_device_is_not_cached(client, session, respond):
    session.request.side_effect = [respond(500), respond()]
    api = client.insertion_api()
    with pytest.raises(ApiError):
        api.register_device("dev")
    assert api.register_device("dev")  # retried, not skipped
    assert session.request.call_count == 2
    assert not api.register_device("dev")


def test_register_device_unknown_type_is_dropped(client, session, respond, sent_json):
    session.request.side_effect = [respond(body=["OTHER"]), respond()]
    assert client.insertion_api().register_device("dev", device_type="CUSTOM", always_update=True)
    assert sent_json() == {"featureOfInterest": {"name": "dev"}}
