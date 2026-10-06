import json
import requests
from flythings.base_client import BaseClient
from flythings.paths import DEVICE_ALERT_URL


class UtilModule(BaseClient):
    def __init__(self, config):
        super().__init__(config)

    def api_get_request(self, url):
        response = requests.get(self.config.server + url, headers=self.headers, timeout=self.config.timeout)
        if response is not None:
            if response.status_code >= 400:
                response.status_code, response.text
        else:
            print("NO RESPONSE FROM SERVICE")
            return 502
        return response.status_code, json.loads(response.text)

    def send_alert(self, subject, text):
        response = requests.put(self.config.server + DEVICE_ALERT_URL, data=json.dumps({
            "subject": subject,
            "text": text
        }), headers=self.headers)
        return response.status_code, json.loads(response.text)
