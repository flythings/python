# Migrating to 3.0

[Back to the README](../README.md) · [3.0 verification status](Verification.md)

3.0 replaces both earlier APIs: the module-level functions of 2.2.x (`import flythings as fly; fly.send_observation(...)`) and the unreleased `*Module` classes that shared class-level state. Now:

- One `FlyThings` client hands out the feature APIs.
- Credentials live in immutable `Connection` values; for several servers or users, create one client per connection.
- Errors are raised instead of printed or returned as status codes.

## Before and after

```python
# 2.x
import flythings as fly

fly.load_data_by_file("Configuration.properties")
fly.set_device("dev1")
fly.set_sensor("sensor")
fly.send_observations([fly.get_observation(20, "temperature"), fly.get_observation(30, "humidity")])
rows = fly.search(42)

# 3.0
from flythings import FlyThings, Observation

with FlyThings.from_config_file("Configuration.properties") as client:
    client.insertion_api().send_observations(
        [Observation(client.series("temperature"), 20), Observation(client.series("humidity"), 30)]
    )
    points = client.query_api().search_by_id(42)
```

## Behaviour changes

- **Errors raise.** Methods no longer return status codes, `None` or strings such as `'NoAuthenticationError'`. The exceptions are `find_series` and `get_last_observation_before_date`, which still return `None` when there is nothing to return. HTTP errors raise `ApiError`, unreachable servers raise `NetworkError`, missing or rejected credentials raise `AuthenticationError`, socket problems raise `SocketError`, and real-time interval violations raise `RateLimitError`. A missing configuration file raises `FileNotFoundError`, and one without a `server` key raises `ValueError`.
- **No printing.** Messages go to the `flythings` logger.
- **Configuration file.** Values may contain `:`, so `server:https://...` works.

## Method map

| 2.x | 3.0 |
| --- | --- |
| `load_data_by_file(file)` | `FlyThings.from_config_file(file)` |
| `login(user, password, login_type)` | `Connection.login(url, user, password, login_type)` |
| `logout()` | Drop the client or connection |
| `set_server(url)` | `Connection(url, ...)` |
| `set_token(t)`, or `TOKEN` in the configuration file: the `x-auth-token` returned by a login | `Connection(url, session_token=t)` |
| `set_authorization_token(t)`, or `AUTHORIZATION` in the configuration file: a bearer token | `Connection(url, token=t)` |
| `set_workspace(w)` | `Connection(url, ..., workspace=w)` |
| `set_timeout(t)` | `FlyThings(..., timeout=t)` |
| `set_custom_header(name, value)` | Pass `FlyThings(..., session=s)` with `s.headers[name] = value` |
| `get_server()`, `get_headers()` | `client.default.url`, `client.default.headers()` |
| `set_device(name, object, always_update)` | `insertion_api().register_device(name, device_type=..., geom=..., always_update=...)`; default device: `FlyThings(..., device=name)`. Registered devices are recorded in `.foiCache`, the same file and format as 2.x, which is now created on the first registration instead of on import; pass `FlyThings(..., foi_cache=path)` to use another file |
| `set_sensor(name)` | `FlyThings(..., sensor=name)` |
| `get_observation(value, property, ...)` | `Observation(series, value, time, uom=..., ...)` |
| `get_image_observation`, `get_image_bytes_observation`, `get_image_base64_observation` | `Observation.from_file(series, path_or_bytes_or_file, file_format, encoded=...)` |
| `get_observation_csv(value, series_id=..., ...)` | `Observation(...).to_csv()` or `csv_line(series_id, value, time, uom)` |
| `send_observation(value, property, ...)` | `insertion_api().send_observation(Observation(...))` |
| `send_observations(values)` | `insertion_api().send_observations(observations)` |
| `send_observations_csv(values)` | `insertion_api().send_observations_csv(lines)` |
| `send_record(series_id, observations)` | `insertion_api().send_record(series_id, observations)` |
| `send_prediction(insertion_module, value, property, ...)` | `insertion_api().send_prediction(Observation(...))` |
| `send_predictions(values)` | `insertion_api().send_predictions(observations)` |
| `search(series_id, start, end, aggrupation, aggrupation_type)` | `query_api().search_by_id(series_id, start, end, aggregation=..., aggregation_type=...)`, which returns the same `{"value", "time"}` dicts, keys in the same order, or `search_observations([series, ...])` for several series, whose dicts add `"foi"`, `"procedure"` and `"observable_property"` |
| `search_prediction(...)` | `query_api().search_predictions_by_id(...)` or `search_predictions([series, ...])` |
| `find_series(foi, procedure, property)` | `query_api().find_series(Series(foi, procedure, property))` |
| `get_last_observation_before_date(series_id, ts)` | `query_api().get_last_observation_before_date(series_id, ts)`, which returns `{"time", "value"}` instead of a tuple, or `None` as before |
| `send_socket(series_id, value, ts, protocol)` | `rt = realtime_api()` once, then `rt.send(series_id, value, ts, protocol)`; each `realtime_api()` call opens its own sockets. `protocol` defaults to `"TCP"`; where 2.x code passed `None`, omit it, since `None` now raises `ValueError` |
| `set_batch_enabled(True)` | `realtime_api(WriteOptions(batch=True))` |
| `register_action`, `register_action_for_series` | `actions = actions_api()` once, then `actions.register_action(...)`, `actions.register_action_for_series(...)`; these return nothing and raise on error. Each `actions_api()` call returns a new API with its own actions, so register, listen and report progress on the same one |
| `start_action_listening(foi)`, `stop_action_listening()` | `actions.start_listening(foi)`, `actions.stop_listening()`. As in 2.x, the listener keeps the program running until it is stopped |
| `send_progress_action(message)` | `actions.send_progress(message)` |
| `save_text_metadata`, `save_date_metadata` | `sos_api().save_text_metadata(...)`, `save_date_metadata(...)` |
| `get_text_metadata(key, value, tag_id)` | `text_metadata(key, value, tag_id)` |
| `get_infrastructure(...)`, `get_infrastructure_withmetadata(...)` | `infrastructure(..., text_metadata=[...])` |
| `save_infrastructure*`, `link_device_to_infrastructure` | Same names on `sos_api()`; save methods return the server's response only |
| `api_get_request(url)` | `util_api().get(path)` |
| `send_alert(subject, text)` | `util_api().send_alert(subject, text)` |
