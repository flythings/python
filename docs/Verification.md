# 3.0 verification status

[Back to the README](../README.md) · [Migrating to 3.0](Migration.md)

3.0 rewrites the whole client, so every API needs a check against a live FlyThings server before release. This page tracks that work. When you check an item, tick it and add the date and the server you used (for example `beta`). If something fails, open an issue and link it next to the item. Remove this page once 3.0 is released.

## What has been checked so far

Everything below has been checked **offline only**:

- The test suite (`uv run pytest`) covers every API with mocked HTTP and sockets.
- The same calls were made through 2.2.8 and through 3.0 with the network mocked, and the requests compared one by one (method, URL, headers and JSON body). They match, except for the deliberate changes listed in [Migrating to 3.0](Migration.md).

Nothing has been run against a live server yet. Offline checks cannot tell whether the server answers the way the code assumes; those assumptions are marked **Server assumption** below and are the most important items to check.

[examples/flythings_example.py](../examples/flythings_example.py) runs one call per API. Fill in its placeholders locally, and do not commit real servers, tokens or devices.

## Client and `Connection`

- [ ] `Connection.login(..., login_type="USER")` returns a working connection, and requests carry the workspace the server returned.
- [ ] `Connection.login(..., login_type="DEVICE")` works.
- [ ] A bearer token works: `Connection(url, token=...)`.
- [ ] A session token works: `Connection(url, session_token=...)`.
- [ ] `FlyThings.from_config_file` loads an existing 2.x `Configuration.properties` without changes, with each kind of credential: `user`/`password`, `authorization`, `token`.
- [ ] A wrong token raises `AuthenticationError`, and an unreachable server raises `NetworkError`.
- [ ] **Server assumption:** 3.0 reuses one HTTP session, so it sends back any cookies the server sets; 2.x opened a new session on every request. Check that a long run of requests still behaves.
- [ ] **Server assumption:** after a user login without a workspace, 3.0 sends no `Workspace` header, where 2.x sent an empty one.

## InsertionApi

- [ ] `send_observation` with every field: `uom`, `time`, `geom`, `device_type`, `foi_name`, `force_type`.
- [ ] `send_observations` with more than 1000 values (they are sent in chunks of 1000).
- [ ] `send_prediction` and `send_predictions`.
- [ ] `send_record` with a list and with a string.
- [ ] `send_observations_csv` with lines from `Observation.to_csv()` and from `csv_line()`.
- [ ] `Observation.from_file` with a path, with bytes, and with `encoded=True`.
- [ ] `register_device` with `device_type` and `geom`.
- [ ] `register_device` records the device in `.foiCache`, and a second run from the same directory does not register it again. The file is not created until a device is registered.
- [ ] With an existing 2.x `.foiCache`, devices already listed in it are not registered again.
- [ ] **Server assumption:** calling `register_device` for a device that already exists succeeds (2xx), for example with `always_update=True` or from a directory without the cache file.

## QueryApi

- [ ] `search_by_id` returns the same values as 2.x `search`, with and without dates.
- [ ] `search_by_id` with `aggregation`/`aggregation_type`, and with `as_incremental=True`.
- [ ] `search_predictions_by_id`.
- [ ] **Server assumption:** `search_observations` and `search_predictions` match results using the response fields `foiIdentifier`, `procedure` and `observablePropertyIdentifier`, which no earlier version read. If those names are wrong, the search returns an empty list without an error. Search two series and check that both appear.
- [ ] `find_series` for an existing series returns its `id`.
- [ ] **Server assumption:** `find_series` for a missing series returns `None` (the server answers 400 or 404).
- [ ] `find_series` with names containing spaces, accents, `+`, `(`, `)` and `:`. 3.0 escapes them in the URL; the server should decode them to the same names.
- [ ] `get_last_observation_before_date` returns `{"time", "value"}`, and `None` when there is no earlier value.

## RealTimeApi

- [ ] `send` over TCP with a session token and with a bearer token.
- [ ] `send` over UDP with a session token.
- [ ] **Server assumption:** `send` over UDP with a bearer token. 3.0 sends `Bearer <token>` in the message's `X-AUTH-TOKEN` field; 2.x sent `-`, which could not authenticate.
- [ ] Two direct sends less than 1400 ms apart raise `RateLimitError`.
- [ ] Batching (`WriteOptions(batch=True)`): values arrive, grouped by series.
- [ ] Batching with past timestamps (a backfill) queues every value and the server stores them.
- [ ] Values still queued are sent by `close()`, and by the exit hook when the program ends without `close()`.
- [ ] After the server drops the socket, the next send or batch opens a new one.

## ActionsApi

- [ ] `register_action` and `register_action_for_series` create the action on the server.
- [ ] **Server assumption:** registering an action that already exists on the server (for example, after restarting the program) succeeds.
- [ ] A triggered action runs its callback, for each `ActionDataTypes` value used in practice.
- [ ] **Server assumption:** the parameter of `JSON`, `DATE`, `FILE` and `LIVE` actions arrives as a string, or as whatever 2.x passed. 3.0 passes it on unchanged, as 2.x did.
- [ ] Returning `0` or a string from a callback reports the result in the platform.
- [ ] `send_progress` reports progress while an action runs.
- [ ] A script that ends right after `start_listening()` keeps running and serving actions, as in 2.x.
- [ ] `stop_listening()` and `close()` end the listener promptly.
- [ ] After the server restarts, the listener reconnects (about 30 s later).

## SosApi

- [ ] `save_text_metadata` and `save_date_metadata`, on the client's device and on another device.
- [ ] `save_infrastructure` with text metadata and devices.
- [ ] `save_infrastructure` with an `infrastructure_id` updates the existing infrastructure. This failed in 2.x.
- [ ] `save_infrastructure_without_override_fois` keeps the existing device list.
- [ ] **Server assumption:** `infrastructure(..., text_metadata=[])` sends an empty list, as 2.x did. Check what the server does with it (clears the metadata or leaves it).
- [ ] `link_device_to_infrastructure`.

## UtilApi

- [ ] `get` on a known path, for example `/featureofinterest/devicetypes`.
- [ ] `send_alert`.
