import base64
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO

from flythings._time import Timestamp, now_millis, to_millis
from flythings.schemas import FilePayload, Geometry, JsonValue, ObservationPayload, SeriesQuery


@dataclass(frozen=True)
class Series:
    """A FlyThings series: device (foi), sensor (procedure) and observable property."""

    foi: str
    procedure: str
    observable_property: str
    as_incremental: bool = False

    def to_query(self) -> SeriesQuery:
        return {
            "foi": self.foi,
            "procedure": self.procedure,
            "observableProperty": self.observable_property,
            "asIncremental": self.as_incremental,
        }


@dataclass(frozen=True)
class Observation:
    """One value of a series. Used both for observations and for predictions.

    Build file (image) observations with `Observation.from_file`.
    """

    series: Series
    value: JsonValue
    time: Timestamp | None = None
    uom: str | None = field(default=None, kw_only=True)
    geom: Geometry | None = field(default=None, kw_only=True)
    device_type: str | None = field(default=None, kw_only=True)
    foi_name: str | None = field(default=None, kw_only=True)
    force_type: str | None = field(default=None, kw_only=True)
    file: FilePayload | None = field(default=None, kw_only=True)

    @classmethod
    def from_file(
        cls,
        series: Series,
        content: str | Path | bytes | IO[bytes],
        file_format: str | None = None,
        time: Timestamp | None = None,
        *,
        encoded: bool = False,
        uom: str | None = None,
        geom: Geometry | None = None,
        device_type: str | None = None,
        foi_name: str | None = None,
    ) -> "Observation":
        """Observation carrying a file, for example an image.

        `content` is a path, bytes or a binary file object. With `encoded=True` its content is already base64 and is
        sent as is.
        `file_format` defaults to the path suffix.
        """
        if isinstance(content, (str, Path)):
            path = Path(content)
            raw = path.read_bytes()
            file_format = file_format or path.suffix.removeprefix(".") or None
        elif isinstance(content, bytes):
            raw = content
        else:
            raw = content.read()
        data = raw if encoded else base64.b64encode(raw)
        if not file_format:
            msg = "file_format is required when it cannot be inferred from a file name"
            raise ValueError(msg)
        return cls(
            series,
            None,
            time,
            uom=uom,
            geom=geom,
            device_type=device_type,
            foi_name=foi_name,
            file={"file": data.decode("utf-8"), "format": file_format},
        )

    def to_payload(self) -> ObservationPayload:
        payload: ObservationPayload = {
            "observableProperty": self.series.observable_property,
            "procedure": self.series.procedure,
            "foi": self.series.foi,
        }
        if self.file is not None:
            payload["file"] = self.file
        else:
            payload["value"] = self.value
        if self.uom is not None:
            payload["uom"] = self.uom
        if self.time is not None:
            payload["time"] = to_millis(self.time)
        if self.geom is not None:
            payload["geom"] = self.geom
        if self.device_type is not None:
            payload["deviceType"] = self.device_type
        if self.foi_name is not None:
            payload["foiName"] = self.foi_name
        if self.force_type is not None:
            payload["forceType"] = self.force_type
        return payload

    def to_csv(self) -> str:
        """Line for `InsertionApi.send_observations_csv`: `foi;procedure;property;time;value[;uom]`."""
        if self.file is not None:
            msg = "File observations cannot be sent as CSV"
            raise ValueError(msg)
        prefix = f"{self.series.foi};{self.series.procedure};{self.series.observable_property}"
        return _csv(prefix, self.value, self.time, self.uom)


def csv_line(series_id: int, value: JsonValue, time: Timestamp | None = None, uom: str | None = None) -> str:
    """CSV line addressing the series by ID: `series_id;time;value[;uom]`."""
    return _csv(str(series_id), value, time, uom)


def _csv(prefix: str, value: JsonValue, time: Timestamp | None, uom: str | None) -> str:
    ts = now_millis() if time is None else to_millis(time)
    line = f"{prefix};{ts};{value}"
    if uom is not None:
        line += f";{uom}"
    return line
