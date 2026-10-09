from collections.abc import Mapping
from enum import Enum
from typing import TYPE_CHECKING, Any

from flythings._http import json_or_text
from flythings.connection import Connection
from flythings.paths import (
    DEVICE_METADATA_URL,
    PUBLISH_INFRASTRUCTURE,
    PUBLISH_INFRASTRUCTURE_METADATA,
    PUBLISH_INFRASTRUCTURE_SIMPLE,
    segment,
)
from flythings.schemas import Geometry, Infrastructure, JsonValue, Metadata, MetadataType, SamplingFeature

if TYPE_CHECKING:
    from flythings.client import FlyThings


class SamplingFeatureType(Enum):
    POINT = {"id": 1, "type": "http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingPoint"}  # noqa: RUF012
    LINE = {"id": 2, "type": "http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingSurface"}  # noqa: RUF012
    POLYGON = {"id": 3, "type": "http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_Specimen"}  # noqa: RUF012
    NO_POSITION = {"id": 4, "type": "http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingCurve"}  # noqa: RUF012

    @property
    def feature(self) -> SamplingFeature:
        return {"id": self.value["id"], "type": self.value["type"]}


def text_metadata(key: str, value: str, tag_id: int | None = None) -> Metadata:
    """Text metadata entry for `infrastructure(text_metadata=[...])`."""
    return {"key": key.upper(), "value": value, "tagId": tag_id, "type": "TEXT"}


def infrastructure(
    name: str,
    type: str,  # noqa: A002 (API field name)
    geom: Geometry | None = None,
    geom_type: SamplingFeatureType | None = None,
    fois: list[str] | None = None,
    alias: str | None = None,
    text_metadata: list[Metadata] | None = None,
) -> Infrastructure:
    """Infrastructure (feature tag) document for the `SosApi.save_infrastructure*` methods."""
    result: Infrastructure = {
        "name": name,
        "type": type,
        "geomType": (geom_type or SamplingFeatureType.NO_POSITION).feature,
    }
    if alias is not None:
        result["alias"] = alias
    if geom is not None:
        result["geom"] = geom
    if fois:
        result["featureOfInterestList"] = fois
    if text_metadata is not None:  # an empty list is sent, as in 2.x
        result["textMetadata"] = text_metadata
    return result


class SosApi:
    """Device metadata and infrastructures (feature tags)."""

    def __init__(self, client: "FlyThings", connection: Connection) -> None:
        self._client = client
        self._connection = connection

    def save_text_metadata(self, key: str, value: str, foi: str | None = None) -> None:
        self._save_metadata(key, value, "TEXT", foi)

    def save_date_metadata(self, key: str, value: str, foi: str | None = None) -> None:
        self._save_metadata(key, value, "DATE", foi)

    def save_infrastructure(self, infrastructure: Infrastructure, infrastructure_id: int | None = None) -> JsonValue:
        """Create or update an infrastructure, including its metadata and devices. Returns the server's response."""
        return self._post_infrastructure(PUBLISH_INFRASTRUCTURE_METADATA, infrastructure, infrastructure_id)

    def save_infrastructure_with_metadata(
        self, infrastructure: Infrastructure, infrastructure_id: int | None = None
    ) -> JsonValue:
        """Same request as `save_infrastructure` (kept for 2.x callers)."""
        return self.save_infrastructure(infrastructure, infrastructure_id)

    def save_infrastructure_without_override_fois(
        self, infrastructure: Infrastructure, infrastructure_id: int | None = None
    ) -> JsonValue:
        """Create or update an infrastructure without replacing its device list."""
        return self._post_infrastructure(PUBLISH_INFRASTRUCTURE_SIMPLE, infrastructure, infrastructure_id)

    def link_device_to_infrastructure(self, infrastructure_tree: Mapping[str, Any], foi_identifier: str) -> None:
        path = f"{PUBLISH_INFRASTRUCTURE}/link/featureofinterest/{segment(foi_identifier)}"
        self._client.request("PUT", path, connection=self._connection, body=dict(infrastructure_tree))

    def _save_metadata(self, key: str, value: str, kind: MetadataType, foi: str | None) -> None:
        body: Metadata = {"key": key.upper(), "value": value, "type": kind}
        path = f"{DEVICE_METADATA_URL}/identifier/{segment(self._client.require_device(foi))}"
        self._client.request("PUT", path, connection=self._connection, body=body)

    def _post_infrastructure(
        self, path: str, infrastructure: Infrastructure, infrastructure_id: int | None
    ) -> JsonValue:
        body: Infrastructure = {**infrastructure}
        if infrastructure_id is not None:
            body["id"] = infrastructure_id
        return json_or_text(self._client.request("POST", path, connection=self._connection, body=body))
