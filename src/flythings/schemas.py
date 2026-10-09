"""TypedDicts for the JSON documents exchanged with the FlyThings API.

`TypedDict` and `NotRequired` come from `typing_extensions` so optional keys are reported correctly at runtime on 3.10.
"""

from typing import Any, Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

JsonValue: TypeAlias = str | int | float | bool | list[Any] | dict[str, Any] | None


# Geometry and observations


class Geometry(TypedDict):
    """GeoJSON geometry, for example `{"type": "Point", "crs": "4326", "coordinates": [-8.4, 43.3]}`."""

    type: str
    coordinates: list[Any]
    crs: NotRequired[str]


class FilePayload(TypedDict):
    file: str  # base64
    format: str


class ObservationPayload(TypedDict):
    """One observation or prediction. Carries either `value` or `file`."""

    observableProperty: str
    foi: str
    procedure: str
    value: NotRequired[JsonValue]
    file: NotRequired[FilePayload]
    uom: NotRequired[str]
    time: NotRequired[int]
    geom: NotRequired[Geometry]
    deviceType: NotRequired[str]
    foiName: NotRequired[str]
    forceType: NotRequired[str]


class ObservationsBody(TypedDict):
    observations: list[ObservationPayload]


class PredictionsBody(TypedDict):
    predictions: list[ObservationPayload]


# Search


class SeriesQuery(TypedDict):
    foi: str
    procedure: str
    observableProperty: str
    asIncremental: bool


class SeriesIdQuery(TypedDict):
    id: int
    asIncremental: bool


class SearchRequest(TypedDict):
    series: list[SeriesQuery] | list[SeriesIdQuery]
    startDate: int | None
    endDate: int
    temporalScale: NotRequired[str]
    temporalScaleType: NotRequired[str]


class SearchResultSeries(TypedDict):
    foiIdentifier: str
    procedure: str
    observablePropertyIdentifier: str


class SearchResultItem(TypedDict):
    series: SearchResultSeries
    data: list[list[Any]]  # [time_ms, value] or [time_ms, value, observation_id]


class LastValue(TypedDict):
    time: int
    value: JsonValue


class FoundSeries(TypedDict):
    """Series description returned by `/series/`. Only `id` is relied upon; the server sends more fields."""

    id: int


# Authentication


class LoginResponse(TypedDict):
    token: str
    workspace: NotRequired[str | int]


# Devices


class DeviceFeature(TypedDict):
    name: str
    geom: NotRequired[Geometry]


class DeviceRegistration(TypedDict):
    featureOfInterest: DeviceFeature
    device: NotRequired[str]


# Actions


class ActionOption(TypedDict):
    """One choice of a `SELECTOR` action: `name` is shown to users, `value` is sent to the device."""

    name: str
    value: str


class ActionRegistration(TypedDict):
    name: str
    featureOfInterest: str
    parameterType: str | None
    procedure: NotRequired[str]
    observableProperty: NotRequired[str]
    unit: NotRequired[str]
    alias: NotRequired[str]
    actionOptions: NotRequired[list[ActionOption]]
    jsonTemplate: NotRequired[str]


class ActionMessage(TypedDict):
    """Command received on the action socket."""

    timestamp: int
    name: str
    actionLog: JsonValue
    action: NotRequired[JsonValue]


# SOS: metadata and infrastructures


MetadataType = Literal["TEXT", "DATE"]


class Metadata(TypedDict):
    key: str
    value: str
    type: MetadataType
    tagId: NotRequired[int | None]


class SamplingFeature(TypedDict):
    id: int
    type: str


class Infrastructure(TypedDict):
    name: str
    type: str
    geomType: SamplingFeature
    id: NotRequired[int]
    alias: NotRequired[str]
    geom: NotRequired[Geometry]
    featureOfInterestList: NotRequired[list[str]]
    textMetadata: NotRequired[list[Metadata]]


class Alert(TypedDict):
    subject: str
    text: str


# Real-time sockets


class RealTimePoint(TypedDict):
    seriesId: int
    timestamp: int
    value: JsonValue


class RealTimeMessage(TypedDict):
    seriesId: int
    obs: list[RealTimePoint]


UdpMessage = TypedDict("UdpMessage", {"X-AUTH-TOKEN": str, "data": RealTimeMessage})
