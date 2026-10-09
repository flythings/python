import json

import pytest

from flythings import AuthenticationError, Series
from flythings.apis.query import DEFAULT_RANGE_MS
from flythings.paths import GET_LAST_VALUE_URL, GET_OBSERVATIONS_URL, GET_PREDICTIONS_URL, SERIES_URL


def result(series, data):
    return {
        "series": {
            "foiIdentifier": series.foi,
            "procedure": series.procedure,
            "observablePropertyIdentifier": series.observable_property,
        },
        "data": data,
    }


@pytest.mark.parametrize(
    ("method", "path"), [("search_observations", GET_OBSERVATIONS_URL), ("search_predictions", GET_PREDICTIONS_URL)]
)
def test_search_tags_rows(client, session, respond, method, path):
    temperature = Series("d1", "s", "temperature", as_incremental=True)
    power = Series("d2", "s", "power")
    session.request.return_value = respond(
        body=[
            result(temperature, [[1, 20.5], [2, 21, 777]]),  # the server may append the observation id
            result(power, [[1, 5]]),
            result(Series("x", "y", "z"), [[4, 0]]),
        ]
    )

    rows = getattr(client.query_api(), method)(
        [temperature, power, temperature], start=10, end=20, aggregation="HOUR", aggregation_type="AVG"
    )

    assert rows == [
        {"foi": "d1", "procedure": "s", "observable_property": "temperature", "time": 1, "value": 20.5},
        {"foi": "d1", "procedure": "s", "observable_property": "temperature", "time": 2, "value": 21},
        {"foi": "d2", "procedure": "s", "observable_property": "power", "time": 1, "value": 5},
    ]
    (call,) = session.request.call_args_list
    assert call.args == ("POST", client.default.url + path)
    assert json.loads(call.kwargs["data"]) == {
        "series": [temperature.to_query(), power.to_query()],
        "startDate": 10,
        "endDate": 20,
        "temporalScale": "HOUR",
        "temporalScaleType": "AVG",
    }


def test_search_default_range(client, session, respond, sent_json):
    session.request.return_value = respond(body=[])
    client.query_api().search_observations([Series("d", "s", "p")])
    body = sent_json()
    assert body["endDate"] - body["startDate"] == DEFAULT_RANGE_MS
    client.query_api().search_observations([Series("d", "s", "p")], end=5)
    body = sent_json()
    assert (body["startDate"], body["endDate"]) == (None, 5)
    client.query_api().search_observations([Series("d", "s", "p")], start=5)
    body = sent_json()
    assert body["startDate"] == 5
    assert body["endDate"] > 5


def test_search_rejects_ambiguous_series(client):
    with pytest.raises(ValueError, match="twice"):
        client.query_api().search_observations([Series("d", "s", "p"), Series("d", "s", "p", as_incremental=True)])


@pytest.mark.parametrize(
    ("method", "path"), [("search_by_id", GET_OBSERVATIONS_URL), ("search_predictions_by_id", GET_PREDICTIONS_URL)]
)
def test_search_by_id(client, session, respond, method, path, sent_json):
    session.request.return_value = respond(body=[{"series": {}, "data": [[1, 2.0], [3, 4.0, 777]]}])
    points = getattr(client.query_api(), method)(42, 1, 2, as_incremental=True)
    assert points == [{"time": 1, "value": 2.0}, {"time": 3, "value": 4.0}]
    # The keys 2.x `search` returned, in its order, so DataFrame columns do not swap
    assert [list(p) for p in points] == [["value", "time"], ["value", "time"]]
    assert session.request.call_args.args == ("POST", client.default.url + path)
    assert sent_json() == {
        "series": [{"id": 42, "asIncremental": True}],
        "startDate": 1,
        "endDate": 2,
    }
    session.request.return_value = respond(body=[])
    assert getattr(client.query_api(), method)(42) == []


def test_find_series(client, session, respond):
    session.request.return_value = respond(body={"id": 5})
    series = Series("d", "s", "p")
    assert client.query_api().find_series(series) == {"id": 5}
    assert session.request.call_args.args == ("GET", f"{client.default.url}{SERIES_URL}d/s/p")

    for status in (400, 404):
        session.request.return_value = respond(status)
        assert client.query_api().find_series(series) is None

    session.request.return_value = respond(500)
    with pytest.raises(Exception, match="500"):
        client.query_api().find_series(series)


def test_find_series_escapes_names(client, session, respond):
    session.request.return_value = respond(body={"id": 5})
    client.query_api().find_series(Series("line 1/a", "temp#2", "T?"))
    assert session.request.call_args.args[1] == f"{client.default.url}{SERIES_URL}line%201%2Fa/temp%232/T%3F"


def test_get_last_observation_before_date(client, session, respond):
    session.request.return_value = respond(body={"time": 1, "value": 2})
    assert client.query_api().get_last_observation_before_date(5, 100) == {"time": 1, "value": 2}
    assert session.request.call_args.args == ("GET", f"{client.default.url}{GET_LAST_VALUE_URL}/5/100")

    session.request.return_value = respond()
    assert client.query_api().get_last_observation_before_date(5, 100) is None


@pytest.mark.parametrize("status", [204, 400, 404, 500])
def test_get_last_observation_before_date_none_unless_200(client, session, respond, status):
    session.request.return_value = respond(status, body={"time": 1, "value": 2})
    assert client.query_api().get_last_observation_before_date(5, 100) is None


def test_get_last_observation_before_date_rejected_credentials(client, session, respond):
    session.request.return_value = respond(401)
    with pytest.raises(AuthenticationError):
        client.query_api().get_last_observation_before_date(5, 100)
