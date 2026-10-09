import logging
from collections.abc import Iterable
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING

from typing_extensions import TypedDict

from flythings._http import json_or_none
from flythings._time import Timestamp, now_millis, to_millis
from flythings.connection import Connection
from flythings.errors import ApiError
from flythings.paths import GET_LAST_VALUE_URL, GET_OBSERVATIONS_URL, GET_PREDICTIONS_URL, SERIES_URL, segment
from flythings.schemas import (
    FoundSeries,
    JsonValue,
    LastValue,
    SearchRequest,
    SearchResultItem,
    SeriesIdQuery,
    SeriesQuery,
)
from flythings.series import Series

if TYPE_CHECKING:
    from flythings.client import FlyThings

logger = logging.getLogger(__name__)

DEFAULT_RANGE_MS = int(timedelta(weeks=1).total_seconds() * 1000)


class Row(TypedDict):
    """One value returned by a search of several series, tagged with the names of its series.

    Flat, so `pandas.DataFrame(rows)` gives one column per key.
    """

    foi: str
    procedure: str
    observable_property: str
    time: int
    value: JsonValue


class Point(TypedDict):
    """One value of a series searched by ID: the `{"value", "time"}` dict that 2.x `search` returned.

    The keys keep the 2.x order, so `pandas.DataFrame(points)` has the same columns.
    """

    value: JsonValue
    time: int


class QueryApi:
    """Search observations and predictions, and look up series."""

    def __init__(self, client: "FlyThings", connection: Connection) -> None:
        self._client = client
        self._connection = connection

    def search_observations(
        self,
        series: Iterable[Series],
        start: Timestamp | None = None,
        end: Timestamp | None = None,
        *,
        aggregation: str | None = None,
        aggregation_type: str | None = None,
    ) -> list[Row]:
        """Observations of every series between `start` and `end`, in one request.

        Without dates, the last week is searched; otherwise `end` defaults to now and a missing `start` is
        sent empty. Series must not repeat the same foi/procedure/property with different `as_incremental`,
        since results are matched on those three.
        """
        return self._search(GET_OBSERVATIONS_URL, series, start, end, aggregation, aggregation_type)

    def search_predictions(
        self,
        series: Iterable[Series],
        start: Timestamp | None = None,
        end: Timestamp | None = None,
        *,
        aggregation: str | None = None,
        aggregation_type: str | None = None,
    ) -> list[Row]:
        """Like `search_observations`, for predictions."""
        return self._search(GET_PREDICTIONS_URL, series, start, end, aggregation, aggregation_type)

    def search_by_id(
        self,
        series_id: int,
        start: Timestamp | None = None,
        end: Timestamp | None = None,
        *,
        as_incremental: bool = False,
        aggregation: str | None = None,
        aggregation_type: str | None = None,
    ) -> list[Point]:
        """Observations of one series addressed by its ID."""
        return self._search_by_id(
            GET_OBSERVATIONS_URL, series_id, start, end, as_incremental, aggregation, aggregation_type
        )

    def search_predictions_by_id(
        self,
        series_id: int,
        start: Timestamp | None = None,
        end: Timestamp | None = None,
        *,
        as_incremental: bool = False,
        aggregation: str | None = None,
        aggregation_type: str | None = None,
    ) -> list[Point]:
        """Predictions of one series addressed by its ID."""
        return self._search_by_id(
            GET_PREDICTIONS_URL, series_id, start, end, as_incremental, aggregation, aggregation_type
        )

    def find_series(self, series: Series) -> FoundSeries | None:
        """Series description (including its `id`), or `None` when the series does not exist."""
        names = (series.foi, series.procedure, series.observable_property)
        path = SERIES_URL + "/".join(segment(name) for name in names)
        try:
            response = self._client.request("GET", path, connection=self._connection)
        except ApiError as e:
            # A missing series: 400 is the only error the API documents here, and 2.x returned None for both
            if e.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND):
                return None
            raise
        return json_or_none(response)

    def get_last_observation_before_date(self, series_id: int, timestamp: Timestamp) -> LastValue | None:
        """Last value of a series strictly before `timestamp`.

        Like 2.x, returns `None` when there is none or the server answers anything but 200. Missing or rejected
        credentials (401/403) still raise `AuthenticationError`, and an unreachable server `NetworkError`.
        """
        path = f"{GET_LAST_VALUE_URL}/{series_id}/{to_millis(timestamp)}"
        try:
            response = self._client.request("GET", path, connection=self._connection)
        except ApiError as e:
            logger.debug("No last value for series %s: %s", series_id, e)
            return None
        if response.status_code != HTTPStatus.OK:
            logger.debug("No last value for series %s: HTTP %s", series_id, response.status_code)
            return None
        return json_or_none(response)

    def _search(
        self,
        path: str,
        series: Iterable[Series],
        start: Timestamp | None,
        end: Timestamp | None,
        aggregation: str | None,
        aggregation_type: str | None,
    ) -> list[Row]:
        by_key: dict[tuple[str, str, str], Series] = {}
        for s in dict.fromkeys(series):
            key = (s.foi, s.procedure, s.observable_property)
            if key in by_key:
                msg = f"Series {key} appears twice; results could not be told apart"
                raise ValueError(msg)
            by_key[key] = s
        queries: list[SeriesQuery] = [s.to_query() for s in by_key.values()]
        items = self._post_search(path, queries, start, end, aggregation, aggregation_type)

        rows: list[Row] = []
        for item in items:
            info = item["series"]
            matched = by_key.get((info["foiIdentifier"], info["procedure"], info["observablePropertyIdentifier"]))
            if matched is not None:
                rows.extend(
                    Row(
                        foi=matched.foi,
                        procedure=matched.procedure,
                        observable_property=matched.observable_property,
                        time=int(time),
                        value=value,
                    )
                    for time, value, *_ in item["data"]
                )
        return rows

    def _search_by_id(
        self,
        path: str,
        series_id: int,
        start: Timestamp | None,
        end: Timestamp | None,
        as_incremental: bool,
        aggregation: str | None,
        aggregation_type: str | None,
    ) -> list[Point]:
        queries: list[SeriesIdQuery] = [{"id": series_id, "asIncremental": as_incremental}]
        items = self._post_search(path, queries, start, end, aggregation, aggregation_type)

        if not items:
            return []
        return [Point(value=value, time=int(time)) for time, value, *_ in items[0]["data"]]

    def _post_search(
        self,
        path: str,
        queries: list[SeriesQuery] | list[SeriesIdQuery],
        start: Timestamp | None,
        end: Timestamp | None,
        aggregation: str | None,
        aggregation_type: str | None,
    ) -> list[SearchResultItem]:
        start_ms, end_ms = _date_range(start, end)
        body: SearchRequest = {"series": queries, "startDate": start_ms, "endDate": end_ms}
        if aggregation is not None:
            body["temporalScale"] = aggregation
        if aggregation_type is not None:
            body["temporalScaleType"] = aggregation_type
        return self._client.request("POST", path, connection=self._connection, body=body).json()


def _date_range(start: Timestamp | None, end: Timestamp | None) -> tuple[int | None, int]:
    if start is None and end is None:
        end_ms = now_millis()
        return end_ms - DEFAULT_RANGE_MS, end_ms
    end_ms = now_millis() if end is None else to_millis(end)
    return (None if start is None else to_millis(start)), end_ms
