"""Python client for the FlyThings IoT platform."""

import logging

from flythings.apis.actions import ActionCallback, ActionDataTypes, ActionsApi
from flythings.apis.insertion import InsertionApi, ObservationLike
from flythings.apis.query import Point, QueryApi, Row
from flythings.apis.realtime import RealTimeApi, SocketProtocol, WriteOptions
from flythings.apis.sos import SamplingFeatureType, SosApi, infrastructure, text_metadata
from flythings.apis.util import UtilApi
from flythings.client import FlyThings, FoiCache
from flythings.connection import Connection, Credential, LoginType, Secret
from flythings.errors import (
    ApiError,
    AuthenticationError,
    FlyThingsError,
    NetworkError,
    RateLimitError,
    SocketError,
)
from flythings.schemas import (
    ActionMessage,
    ActionOption,
    ActionRegistration,
    Alert,
    DeviceFeature,
    DeviceRegistration,
    FilePayload,
    FoundSeries,
    Geometry,
    Infrastructure,
    JsonValue,
    LastValue,
    LoginResponse,
    Metadata,
    MetadataType,
    ObservationPayload,
    ObservationsBody,
    PredictionsBody,
    RealTimeMessage,
    RealTimePoint,
    SamplingFeature,
    SearchRequest,
    SearchResultItem,
    SearchResultSeries,
    SeriesIdQuery,
    SeriesQuery,
    UdpMessage,
)
from flythings.series import Observation, Series, csv_line

logging.getLogger("flythings").addHandler(logging.NullHandler())

__all__ = [
    "ActionCallback",
    "ActionDataTypes",
    "ActionMessage",
    "ActionOption",
    "ActionRegistration",
    "ActionsApi",
    "Alert",
    "ApiError",
    "AuthenticationError",
    "Connection",
    "Credential",
    "DeviceFeature",
    "DeviceRegistration",
    "FilePayload",
    "FlyThings",
    "FlyThingsError",
    "FoiCache",
    "FoundSeries",
    "Geometry",
    "Infrastructure",
    "InsertionApi",
    "JsonValue",
    "LastValue",
    "LoginResponse",
    "LoginType",
    "Metadata",
    "MetadataType",
    "NetworkError",
    "Observation",
    "ObservationLike",
    "ObservationPayload",
    "ObservationsBody",
    "Point",
    "PredictionsBody",
    "QueryApi",
    "RateLimitError",
    "RealTimeApi",
    "RealTimeMessage",
    "RealTimePoint",
    "Row",
    "SamplingFeature",
    "SamplingFeatureType",
    "SearchRequest",
    "SearchResultItem",
    "SearchResultSeries",
    "Secret",
    "Series",
    "SeriesIdQuery",
    "SeriesQuery",
    "SocketError",
    "SocketProtocol",
    "SosApi",
    "UdpMessage",
    "UtilApi",
    "WriteOptions",
    "csv_line",
    "infrastructure",
    "text_metadata",
]
