import base64
import io
from datetime import datetime, timezone

import pytest

from flythings import Observation, Series, csv_line

SERIES = Series("device", "sensor", "temperature")


def test_series_query():
    assert Series("d", "s", "p", as_incremental=True).to_query() == {
        "foi": "d",
        "procedure": "s",
        "observableProperty": "p",
        "asIncremental": True,
    }


def test_minimal_payload():
    assert Observation(SERIES, 20).to_payload() == {
        "observableProperty": "temperature",
        "procedure": "sensor",
        "foi": "device",
        "value": 20,
    }


def test_full_payload():
    geom = {"type": "Point", "coordinates": [0, 0]}
    observation = Observation(
        SERIES,
        20,
        1700000000000,
        uom="C",
        geom=geom,
        device_type="type",
        foi_name="name",
        force_type="NUMBER",
    )
    assert observation.to_payload() == {
        "observableProperty": "temperature",
        "procedure": "sensor",
        "foi": "device",
        "value": 20,
        "uom": "C",
        "time": 1700000000000,
        "geom": geom,
        "deviceType": "type",
        "foiName": "name",
        "forceType": "NUMBER",
    }


def test_datetime_time_is_converted_to_millis():
    when = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert Observation(SERIES, 1, when).to_payload().get("time") == 1767225600000


def test_csv_lines():
    assert Observation(SERIES, 20, 1000, uom="C").to_csv() == "device;sensor;temperature;1000;20;C"
    assert Observation(SERIES, 20, 1000).to_csv() == "device;sensor;temperature;1000;20"
    assert csv_line(42, 3.5, 1000) == "42;1000;3.5"
    assert csv_line(42, 3.5).startswith("42;")


def test_file_observation_from_path(tmp_path):
    image = tmp_path / "photo.png"
    image.write_bytes(b"png-bytes")
    payload = Observation.from_file(SERIES, image, time=5).to_payload()
    assert payload.get("file") == {"file": base64.b64encode(b"png-bytes").decode(), "format": "png"}
    assert "value" not in payload
    assert payload.get("time") == 5


@pytest.mark.parametrize(
    ("content", "encoded"),
    [
        (b"raw", False),
        (base64.b64encode(b"raw"), True),
        (io.BytesIO(b"raw"), False),
        (io.BytesIO(base64.b64encode(b"raw")), True),
    ],
)
def test_file_observation_from_bytes_and_streams(content, encoded):
    observation = Observation.from_file(SERIES, content, "jpg", encoded=encoded)
    assert observation.to_payload().get("file") == {"file": base64.b64encode(b"raw").decode(), "format": "jpg"}


def test_file_observation_from_encoded_path(tmp_path):
    encoded = tmp_path / "photo.png"
    encoded.write_bytes(base64.b64encode(b"png-bytes"))
    payload = Observation.from_file(SERIES, encoded, encoded=True).to_payload()
    assert payload.get("file") == {"file": base64.b64encode(b"png-bytes").decode(), "format": "png"}


def test_file_observation_requires_format(tmp_path):
    no_suffix = tmp_path / "photo"
    no_suffix.write_bytes(b"x")
    with pytest.raises(ValueError, match="file_format"):
        Observation.from_file(SERIES, no_suffix)
    with pytest.raises(ValueError, match="file_format"):
        Observation.from_file(SERIES, b"x")


def test_file_observation_cannot_be_csv():
    with pytest.raises(ValueError, match="CSV"):
        Observation.from_file(SERIES, b"x", "png").to_csv()
