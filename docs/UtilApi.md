# UtilApi

[Back to the README](../README.md) · [Client, connections and series](Client.md)

Generic requests and device alerts. Get it with `client.util_api()`.

| Method | Description |
| --- | --- |
| `get(path)` | GETs any API path (for example `/featureofinterest/devicetypes`) and returns the decoded body: JSON, the raw text when it is not JSON, or `None` when it is empty. |
| `send_alert(subject, text)` | Sends an alert from the device. Returns the server's response. |

For other methods or paths, `client.request(method, path, body=...)` sends any authenticated request.
