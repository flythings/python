# Changelog

## 3.0.0a0 (2026-10-09)

3.0 replaces the 2.x API. See [Migrating to 3.0](docs/Migration.md) for the replacement of each 2.x function.

### BREAKING CHANGE

- the module-level functions (`fly.send_observation`, `fly.search`, ...) are gone; use a `FlyThings` client and its APIs
- errors raise (`ApiError`, `AuthenticationError`, `NetworkError`, `SocketError`, `RateLimitError`) instead of printing and returning status codes. Messages go to the `flythings` logger and are not shown unless the program configures logging
- **insertion**: predictions are sent through `insertion_api()` and searched through `query_api()`
- **insertion**: `get_observation` and the `get_image_*_observation` builders are replaced by `Observation(...)` and `Observation.from_file(...)`
- **build**: requires Python 3.10 or newer (2.x declared no minimum) and adds `typing-extensions`; `enum34` is no longer required

### Feat

- **client**: `FlyThings` client with one HTTP session, handing out `insertion_api()`, `query_api()`, `realtime_api()`, `actions_api()`, `sos_api()` and `util_api()`; usable as a context manager
- **client**: immutable `Connection` (server plus credentials), `Series` and `Observation` values. `Connection` stores its tokens as `Secret`, which hides them from `repr`, `str` and logs. Each client works against one connection; create one client per server or user
- **query**: `search_observations` / `search_predictions` search several series in one call and return rows tagged with their device, sensor and property
- **query**: results and JSON documents are typed with `TypedDict`s exported from the package. `search_by_id` returns `Point` dicts, `{"value", "time"}` as 2.x `search` did (same key order), and the multi-series searches return flat `Row` dicts that add `"foi"`, `"procedure"` and `"observable_property"`, so results load directly into a pandas `DataFrame`
- **realtime**: batching is a per-instance `WriteOptions`, with `flush()` and `close()`

### Fix

- **realtime**: enabling batching no longer keeps the program from exiting; values still queued at exit are sent
- **realtime**: UDP sockets connected to the URL scheme instead of the host
- **sos**: `save_infrastructure*` failed when given an ID
- importing the package no longer creates `.foiCache` in the working directory, nor tries to `pip install` missing dependencies. `register_device` still records devices in `.foiCache`, in the same format, creating the file on the first registration; `foi_cache` selects another file
- **client**: every request now has a timeout
- **client**: configuration files accept values containing `:` (URLs with a scheme, passwords, tokens), read `timeout` as a number, and trim the `authorization` value, so the header is no longer `Bearer  <token>`

## 2.2.8
* Include allow to force observation type on get observation.

## 2.2.7
* Include allow to save metadata without overriding fois.

## 2.2.6
* Fix bug fois are not loading on infrastructure update.

## 2.2.5
* Fix compilation error with global headers

## 2.2.4
* Update readme.
* Include alias on get infrastructure methods.
* Include set_authorization on config file.

## 2.2.3
* Allow to send json_template without need a series_action.

## 2.2.2
* Allow to send json_template on action register.

## 2.2.1
* Send observations and predictions on groups of 1000 on multiple insertion.

## 2.2.0
* Include get image observation by file, path, bytes or base64.
* Include logout method.
* Include set_server.
* Return response text on add infrastructure with or without metadata.
* Do nothing on set server if server is None.

## 2.1.1
* Fix SosModule documentation.

## 2.1.0
* Include save infrastructure.
* Include save infrastructure with metadata.
* Include link device to infrastructure.
* Remove create infrastructure with metadata.
* Remove update infrastructure with metadata.

## 2.0.2
* Include create infrastructure with metadata method.
* Include update infrastructure with metadata method.

## 2.0.1
* Include set x-auth-token to - on set_token().
* Fix authorization_token not working on action and realtime.
* Parse server hostname automatically on get_tcp_socket().
* Make set_server method more intelligent to autocomplete the required parts.
* Add metadata becomes save metadata which creates or updates metadata.

## 2.0.0
* Include predictions management methods.
* Refactor all methods to use _ instead of camel case.
* Include a method to set authorization token.
* Refactor send realtime messages to send samples on same format.
* Include batch_enabled as global variable.
* Include more action_types that Flythings Platform Allows.
* Posibilidad de actuaciones de tipo ongoing.

## 1.4.15
* Allow to save device metadata on text and date format.

## 1.4.14
* Include a flag to update always a featureOfInterest

## 1.4.13
* Include recv to clear buffer after send realtime data.

## 1.4.12
* Print response text after send observations to allow to view request errors.

## 1.4.11
* Include send alert device method
* Include send custom get request method
* Support HTTPs or HTTP

## 1.4.10
* Continue supporting Python2

## 1.4.9
* Fix findSeries was trying to load a json outside a try block.

## 1.4.8
* Fix send observations method was returning response if a exception was throw.

## 1.4.7
* Fix a error that action socket gets corrupted and wasn't able to detect that failure.

## 1.4.6
* Fix send record method.
* Include device_type and foi_name on observation construction.

## 1.4.5
* Fix failure setting timeout on TCP socket on socket creation
* Restore compatibility with Python2.7

## 1.4.4
* Include timeout on TCP sockets of 15 seconds.
* Improve code understandability.

## 1.4.3
* Fix pypy.org faulty update.

## 1.4.2
* Not append Unit if is none.
* Not reset the socket on ping exception.


## 1.4.1
* Fix socket never retry reconnect on service restart or turn off.


## 1.4.0
* Include getHeaders() to return current headers.
* Better documentation about action messages.
* Fix pypi.org not parsing property the .md files.
* Rename foi.txt cache foi file to .foiCache.


## 1.3.0
* Return None if login fails.
* Allow actions to send String when the device wants to send a error to the server.
* Refactor acumulateObss, now included on sendSocket if batch is enabled.

## 1.2.3
* Remove pathlib dependency

## 1.2.2
* Checks if user has pathlib installed, if not, installs it.

## 1.2.1
* Checks if user has enum34 installed, if not, installs it.

## 1.2.0
* Include csv observation construction and insertion.
* Actions contains the action creation timestamp.
* Include action alias.
* Include action sequence diagram.

## 1.1.0
* Include batch to allow send multiple observations on real time.
* UpdateDevice() allows new device parameters and persist it on platform.
* Include changelog.
