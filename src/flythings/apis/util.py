from typing import TYPE_CHECKING

from flythings._http import json_or_text
from flythings.connection import Connection
from flythings.paths import DEVICE_ALERT_URL
from flythings.schemas import Alert, JsonValue

if TYPE_CHECKING:
    from flythings.client import FlyThings


class UtilApi:
    """Generic requests and device alerts."""

    def __init__(self, client: "FlyThings", connection: Connection) -> None:
        self._client = client
        self._connection = connection

    def get(self, path: str) -> JsonValue:
        """GET any API path (for example `/featureofinterest/devicetypes`) and return the decoded body."""
        return json_or_text(self._client.request("GET", path, connection=self._connection))

    def send_alert(self, subject: str, text: str) -> JsonValue:
        body: Alert = {"subject": subject, "text": text}
        return json_or_text(self._client.request("PUT", DEVICE_ALERT_URL, connection=self._connection, body=body))
