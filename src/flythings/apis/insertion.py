from collections.abc import Iterable
from itertools import islice
from typing import IO, TYPE_CHECKING, Literal, TypeAlias, cast

from flythings._http import json_or_text
from flythings.connection import Connection
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
from flythings.schemas import (
    DeviceRegistration,
    Geometry,
    JsonValue,
    ObservationPayload,
    ObservationsBody,
    PredictionsBody,
)
from flythings.series import Observation

if TYPE_CHECKING:
    from flythings.client import FlyThings

CHUNK_SIZE = 1000

ObservationLike: TypeAlias = Observation | ObservationPayload
"""An `Observation`, or a payload dict built by hand."""


def _payload(observation: ObservationLike) -> ObservationPayload:
    return observation.to_payload() if isinstance(observation, Observation) else observation


class InsertionApi:
    """Send observations and predictions, and register devices."""

    def __init__(self, client: "FlyThings", connection: Connection) -> None:
        self._client = client
        self._connection = connection

    def send_observations(self, observations: Iterable[ObservationLike]) -> None:
        """Send observations, one request per chunk of 1000.

        Raises on the first failed request; chunks already sent stay stored.
        """
        self._send_bulk(PUBLISH_MULTIPLE_URL, "observations", observations)

    def send_predictions(self, predictions: Iterable[ObservationLike]) -> None:
        """Like `send_observations`, for predictions."""
        self._send_bulk(PUBLISH_PREDICTION_MULTIPLE_URL, "predictions", predictions)

    def send_observation(self, observation: ObservationLike) -> None:
        self._send_single(PUBLISH_SINGLE_URL, observation)

    def send_prediction(self, prediction: ObservationLike) -> None:
        self._send_single(PUBLISH_PREDICTION_SINGLE_URL, prediction)

    def send_record(self, series_id: int, observations: str | list[JsonValue]) -> JsonValue:
        """Send a record (several values at once) to a series by ID. A string is sent as is."""
        path = f"{PUBLISH_RECORD_URL}/{series_id}"
        if isinstance(observations, str):
            response = self._client.request("PUT", path, connection=self._connection, data=observations)
        else:
            response = self._client.request("PUT", path, connection=self._connection, body=observations)
        return json_or_text(response)

    def send_observations_csv(self, lines: str | bytes | IO[str] | IO[bytes] | Iterable[str]) -> JsonValue:
        """Send CSV lines built with `Observation.to_csv` or `csv_line`.

        A string, bytes or an open file (text or binary) is sent as is, as 2.x did; other iterables are joined one
        line per item.
        """
        if isinstance(lines, (str, bytes)):
            data = lines
        elif hasattr(lines, "read"):
            data = cast("IO[str] | IO[bytes]", lines).read()
        else:
            data = "\n".join(line.rstrip("\r\n") for line in cast("Iterable[str]", lines))
        return json_or_text(self._client.request("POST", PUBLISH_PLAIN_CSV_URL, connection=self._connection, data=data))

    def register_device(
        self,
        name: str,
        *,
        device_type: str | None = None,
        geom: Geometry | None = None,
        always_update: bool = False,
    ) -> bool:
        """Create the device (feature of interest) on the server once per client. Returns whether a request was sent.

        `device_type` is only applied when the server knows it.
        """
        foi_cache = self._client.foi_cache
        if foi_cache.contains(self._connection.url, name) and not always_update:
            return False
        body: DeviceRegistration = {"featureOfInterest": {"name": name}}
        if geom is not None:
            body["featureOfInterest"]["geom"] = geom
        if device_type is not None:
            known_types: list[str] = self._client.request("GET", DEVICE_TYPES_URL, connection=self._connection).json()
            if device_type in known_types:
                body["device"] = device_type
        self._client.request("POST", FOI_URL, connection=self._connection, body=body)
        foi_cache.add(self._connection.url, name)
        return True

    def _send_single(self, path: str, observation: ObservationLike) -> None:
        self._client.request("PUT", path, connection=self._connection, body=_payload(observation))

    def _send_bulk(
        self, path: str, key: Literal["observations", "predictions"], observations: Iterable[ObservationLike]
    ) -> None:
        remaining = iter(observations)
        while chunk := [_payload(o) for o in islice(remaining, CHUNK_SIZE)]:
            body: ObservationsBody | PredictionsBody = (
                {"observations": chunk} if key == "observations" else {"predictions": chunk}
            )
            self._client.request("PUT", path, connection=self._connection, body=body)
