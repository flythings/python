# [FlyThings Client](http://flythings.io)

Python client for the FlyThings IoT platform: send and search observations and predictions, stream real-time values, react to device actions and manage device metadata.

## Getting Started

The client requires [Python](https://www.python.org/) 3.10 or newer. Install it from PyPI with [uv](https://docs.astral.sh/uv/) or pip:

```bash
uv add flythings
# or
pip install flythings
```

```python
import time

from flythings import Connection, FlyThings, Observation, Series

with FlyThings(Connection("https://api.flythings.io/api", token="<bearer token>")) as client:
    temperature = Series("<device>", "<sensor>", "temperature")
    client.insertion_api().send_observation(Observation(temperature, 21.5, int(time.time() * 1000), uom="C"))

    for row in client.query_api().search_observations([temperature]):  # last week
        print(row["time"], row["value"])
```

A runnable walkthrough lives in [examples/flythings_example.py](examples/flythings_example.py). Coming from 2.x? See [Migrating to 3.0](docs/Migration.md).

## Several servers at once

A `Connection` is a server URL plus credentials, and a `FlyThings` client works against one connection. To use several servers or users, create one client per connection. Each client has its own HTTP session, so cookies a server sets for one user never reach another.

```python
from flythings import Connection, FlyThings, Series

main = FlyThings(Connection("https://api.flythings.io/api", token="<bearer token>"))
other = FlyThings(Connection("https://<other server>/api", token="<other bearer token>"))

with main, other:
    rows = main.query_api().search_observations([Series("dev1", "sensor", "temperature")])
    other_rows = other.query_api().search_observations([Series("dev2", "sensor", "power")])
```

Pass your own `requests.Session` with `session=` only for HTTP settings such as retries, proxies or custom headers, and do not share it between clients with different credentials: a session keeps the cookies servers set, so one user's cookies would be sent with another user's requests. A client never closes a session it was given.

## Configuration file

`FlyThings.from_config_file("Configuration.properties")` reads `key:value` lines (keys are case-insensitive):

| Key | Description |
| --- | --- |
| `server` | Server URL. Required. |
| `authorization` | Bearer token, as `Connection(url, token=...)`. |
| `token` | Session token (`x-auth-token`), as `Connection(url, session_token=...)`; used when there is no `authorization`. |
| `user`, `password` | Log in with these instead of a token. Storing a password in a file is not recommended. |
| `login_type` | `USER` (default) or `DEVICE`. |
| `device`, `sensor` | Defaults for `client.series(...)`, the actions API and device metadata. |
| `timeout` | Request timeout in seconds. Default `1000`. |

```properties
SERVER:https://api.flythings.io/api
AUTHORIZATION:<put your token here>
DEVICE:Python
SENSOR:Client
TIMEOUT:30
```

## Documentation

A `FlyThings` client holds one connection (server and credentials) and hands out one API per feature area. [Client, connections and series](docs/Client.md) covers the client itself, `Connection`, `Series`, `Observation`, errors and types.

| API | Get it with | Use it to | Main methods |
| --- | --- | --- | --- |
| [InsertionApi](docs/InsertionApi.md) | `client.insertion_api()` | Send observations and predictions over HTTP, and register devices | `send_observation(s)`, `send_prediction(s)`, `send_record`, `send_observations_csv`, `register_device` |
| [QueryApi](docs/QueryApi.md) | `client.query_api()` | Read observations and predictions back, and look up series | `search_by_id`, `search_observations`, `search_predictions`, `find_series`, `get_last_observation_before_date` |
| [RealTimeApi](docs/RealTimeApi.md) | `client.realtime_api(write_options)` | Stream values to series over TCP/UDP sockets, optionally batched | `send`, `flush`, `close` |
| [ActionsApi](docs/ActionsApi.md) | `client.actions_api(device)` | Let the platform trigger functions on a device | `register_action`, `register_action_for_series`, `start_listening`, `stop_listening`, `send_progress` |
| [SosApi](docs/SosApi.md) | `client.sos_api()` | Manage device metadata and infrastructures | `save_text_metadata`, `save_date_metadata`, `save_infrastructure`, `link_device_to_infrastructure` |
| [UtilApi](docs/UtilApi.md) | `client.util_api()` | Call any other endpoint, and send alerts | `get`, `send_alert` |

The real-time and actions APIs keep sockets and threads open; `client.close()` (or a `with` block) stops them.

- [Migrating to 3.0](docs/Migration.md)
- [3.0 verification status](docs/Verification.md): what has been checked against a live server before release
- [Change log](CHANGELOG.md)

## Development

The project is managed with [uv](https://docs.astral.sh/uv/) and uses a `src/` layout.

```bash
uv sync                 # create .venv with the package and dev dependencies
uv tool install pre-commit   # once per machine
pre-commit install           # installs the pre-commit, commit-msg and pre-push hooks
```

| Path             | Contents                                                                     |
| ---------------- | ---------------------------------------------------------------------------- |
| `src/flythings/` | The library package                                                          |
| `tests/`         | Offline unit tests (`*_test.py`), run with pytest                            |
| `examples/`      | Example script against a live server and a sample `Configuration.properties` |
| `docs/`          | API reference, one page per feature API                                      |

Day-to-day commands:

```bash
uv run pytest           # tests with coverage
uv run ruff check       # lint
uv run ruff format      # format
pyrefly check           # type check (uv tool install pyrefly)
uv build                # sdist and wheel into dist/
```

The example script needs real credentials: fill in the placeholders in `examples/flythings_example.py` (or `examples/Configuration.properties`) and run it with `uv run examples/flythings_example.py`. Do not commit real credentials.

### Commits and releases

Commits follow [Conventional Commits](https://www.conventionalcommits.org/) and are checked by a pre-commit hook.

Release tags have no `v` prefix (e.g. `2.2.8`).

## [License](LICENSE)

**Developed by [ITG](http://www.itg.es)**
