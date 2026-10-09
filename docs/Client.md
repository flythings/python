# Client, connections and series

[Back to the README](../README.md)

## `Connection`

A server URL plus the credentials used against it. It is immutable: logging in returns a new value instead of changing the client.

```python
from flythings import Connection

main = Connection("https://api.flythings.io/api", token="<bearer token>")
session = Connection("https://api.flythings.io/api", session_token="<session token>", workspace="<workspace>")
logged_in = Connection.login("https://api.flythings.io/api", "<user>", "<password>", login_type="USER")
```

| Member | Description |
| --- | --- |
| `Connection(url, token=None, *, session_token=None, workspace=None)` | `token` is a bearer token (`Authorization: Bearer ...`), what 2.x set with `set_authorization_token`; `session_token` is the token of a login (`x-auth-token`), what 2.x set with `set_token`. Either token may be given as a plain string or a `Secret`, and is stored as a `Secret`. The `Workspace` header is sent whenever `workspace` is set; it may be a number, as 2.x `set_workspace` took, and is sent as text. The URL is normalized: spaces and the trailing `/` are removed, and `http://` is added when there is no scheme. |
| `Connection.login(url, user, password, login_type="USER", *, workspace=None, session=None, timeout=1000)` | Logs in with a user (`"USER"`) or a device (`"DEVICE"`, case-insensitive) and returns a connection holding the session token. For user logins the workspace comes from the server. Raises `AuthenticationError` when the login is rejected. |
| `headers()` | Headers that authenticate a request on this connection. |
| `is_authenticated` | Whether the connection has a token. |

Two connections are equal when URL and credentials are equal, whether a token was given plain or as a `Secret`.

`Secret(value)` wraps a token so that `repr()`, `str()`, f-strings and logs show `**********`; `get_secret_value()` returns it. Two secrets are equal when their values are, but a `Secret` never equals a plain string.

## `FlyThings`

The client. It holds one connection and one HTTP session, and hands out the feature APIs. For several servers or users, create one client per connection.

```python
from flythings import Connection, FlyThings

with FlyThings(
    Connection("https://api.flythings.io/api", token="<bearer token>"), device="<device>", sensor="<sensor>"
) as client:
    insertion = client.insertion_api()
    query = client.query_api()
```

| Member | Description |
| --- | --- |
| `FlyThings(connection, *, timeout=1000, session=None, device=None, sensor=None, foi_cache=".foiCache")` | `timeout` is in seconds. `session` lets you pass your own `requests.Session` (for example with retries, proxies or custom headers); the client then does not close it. A session keeps cookies, so do not share one between clients with different credentials. `device` and `sensor` are defaults for `series()`, the actions API and device metadata. `foi_cache` is the file where `register_device` remembers registered devices, as in 2.x: `.foiCache` in the working directory by default, or another path or a `FoiCache`. The file is created on the first registration. |
| `FlyThings.from_config_file(path="Configuration.properties", *, session=None, foi_cache=".foiCache")` | Builds a client from a properties file; see the README. |
| `insertion_api()`, `query_api()`, `realtime_api(write_options=None)`, `actions_api(device=None)`, `sos_api()`, `util_api()` | The feature APIs: [InsertionApi](InsertionApi.md), [QueryApi](QueryApi.md), [RealTimeApi](RealTimeApi.md), [ActionsApi](ActionsApi.md), [SosApi](SosApi.md), [UtilApi](UtilApi.md). |
| `series(observable_property, foi=None, procedure=None, *, as_incremental=False)` | Builds a `Series` from the default device and sensor. |
| `require_device(foi=None)`, `require_sensor(procedure=None)` | Return the argument, else the default device or sensor; raise `ValueError` when there is neither. Used by the APIs that fall back to the defaults. |
| `request(method, path, *, connection=None, body=None, data=None)` | Sends an authenticated request on `connection` (default: the client's); `body` is serialized as JSON. Used by the APIs, and available for endpoints the library does not wrap. |
| `close()` / `with` block | Flushes batched real-time values, stops action listeners, closes sockets and, if the client created it, the HTTP session. |

## `Series` and `Observation`

```python
from flythings import Observation, Series

temperature = Series("<device>", "<sensor>", "temperature")

reading = Observation(temperature, 21.5, 1767225600000, uom="C")
photo = Observation.from_file(temperature, "photo.png")
```

| Member | Description |
| --- | --- |
| `Series(foi, procedure, observable_property, as_incremental=False)` | Device, sensor and observable property. |
| `Observation(series, value, time=None, *, uom=None, geom=None, device_type=None, foi_name=None, force_type=None)` | One value. `time` is epoch milliseconds or a `datetime`. `geom` is a GeoJSON dict such as `{"type": "Point", "crs": "4326", "coordinates": [-8.4, 43.3]}`. Used for predictions too. |
| `Observation.from_file(series, content, file_format=None, time=None, *, encoded=False, ...)` | Observation carrying a file (an image, for example). `content` is a path, bytes or a binary file object; with `encoded=True` its content is already base64 and is sent as is. The format defaults to the file suffix. |
| `observation.to_payload()` | The JSON document sent to the server (`ObservationPayload`). |
| `observation.to_csv()` / `csv_line(series_id, value, time=None, uom=None)` | Lines for `InsertionApi.send_observations_csv`. |

## Errors

Every error derives from `FlyThingsError`.

| Error | Raised when |
| --- | --- |
| `AuthenticationError` | The connection has no token, a login is rejected, or the server answers 401/403. |
| `ApiError` | The server answers with another error status. Has `status_code`, `body` and `url`. |
| `NetworkError` | The server cannot be reached: connection failure, timeout or another transport error from `requests`. |
| `SocketError` | A real-time or action socket cannot be opened or fails. |
| `RateLimitError` | A real-time value is sent sooner than the platform allows. |

The library logs through the `flythings` logger and never prints.

## Types

The JSON documents exchanged with the server are typed as `TypedDict`s and exported from `flythings`, for example `ObservationPayload`, `SearchResultItem`, `LastValue`, `Infrastructure` and `Metadata`.
