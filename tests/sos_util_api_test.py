import pytest

from flythings import FlyThings, SamplingFeatureType, infrastructure, text_metadata
from flythings.paths import (
    DEVICE_ALERT_URL,
    DEVICE_METADATA_URL,
    DEVICE_TYPES_URL,
    PUBLISH_INFRASTRUCTURE,
    PUBLISH_INFRASTRUCTURE_METADATA,
    PUBLISH_INFRASTRUCTURE_SIMPLE,
)


@pytest.mark.parametrize(("method", "kind"), [("save_text_metadata", "TEXT"), ("save_date_metadata", "DATE")])
def test_save_metadata(client, session, method, kind, sent_json):
    getattr(client.sos_api(), method)("owner", "me")
    assert session.request.call_args.args == ("PUT", f"{client.default.url}{DEVICE_METADATA_URL}/identifier/device")
    assert sent_json() == {"key": "OWNER", "value": "me", "type": kind}
    getattr(client.sos_api(), method)("owner", "me", foi="other")
    assert session.request.call_args.args[1].endswith("/identifier/other")
    getattr(client.sos_api(), method)("owner", "me", foi="a/b")
    assert session.request.call_args.args[1].endswith("/identifier/a%2Fb")


def test_save_metadata_requires_device(connection, session):
    with pytest.raises(ValueError, match="device"):
        FlyThings(connection, session=session).sos_api().save_text_metadata("k", "v")


def test_builders():
    metadata = text_metadata("owner", "me", 3)
    assert metadata == {"key": "OWNER", "value": "me", "tagId": 3, "type": "TEXT"}
    assert infrastructure("plant", "SITE") == {
        "name": "plant",
        "type": "SITE",
        "geomType": SamplingFeatureType.NO_POSITION.value,
    }
    geom = {"type": "Point", "coordinates": [0, 0]}
    assert infrastructure("plant", "SITE", geom, SamplingFeatureType.POINT, ["d1"], "Plant", [metadata]) == {
        "name": "plant",
        "type": "SITE",
        "geomType": SamplingFeatureType.POINT.value,
        "alias": "Plant",
        "geom": geom,
        "featureOfInterestList": ["d1"],
        "textMetadata": [metadata],
    }
    assert infrastructure("plant", "SITE", text_metadata=[]).get("textMetadata") == []  # sent, as in 2.x


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("save_infrastructure", PUBLISH_INFRASTRUCTURE_METADATA),
        ("save_infrastructure_with_metadata", PUBLISH_INFRASTRUCTURE_METADATA),
        ("save_infrastructure_without_override_fois", PUBLISH_INFRASTRUCTURE_SIMPLE),
    ],
)
def test_save_infrastructure_sets_id_without_mutating(client, session, respond, method, path, sent_json):
    session.request.return_value = respond(body={"id": 3})
    document = infrastructure("plant", "SITE")
    assert getattr(client.sos_api(), method)(document, 3) == {"id": 3}
    assert session.request.call_args.args == ("POST", client.default.url + path)
    assert sent_json()["id"] == 3
    assert "id" not in document


def test_link_device_to_infrastructure(client, session):
    client.sos_api().link_device_to_infrastructure({"id": 1}, "dev")
    assert session.request.call_args.args == (
        "PUT",
        f"{client.default.url}{PUBLISH_INFRASTRUCTURE}/link/featureofinterest/dev",
    )
    client.sos_api().link_device_to_infrastructure({"id": 1}, "a/b")
    assert session.request.call_args.args[1].endswith("/featureofinterest/a%2Fb")


def test_util_get_and_alert(client, session, respond, sent_json):
    session.request.return_value = respond(body=["CUSTOM"])
    assert client.util_api().get(DEVICE_TYPES_URL) == ["CUSTOM"]
    session.request.return_value = respond(text="sent")
    assert client.util_api().send_alert("subject", "text") == "sent"
    assert session.request.call_args.args == ("PUT", client.default.url + DEVICE_ALERT_URL)
    assert sent_json() == {"subject": "subject", "text": "text"}
    session.request.return_value = respond()
    assert client.util_api().get("/x") is None
