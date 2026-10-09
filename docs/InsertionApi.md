# InsertionApi

[Back to the README](../README.md) · [Client, connections and series](Client.md)

Sends observations and predictions, and registers devices. Get it with `client.insertion_api()`.

## Bulk sends

The bulk methods send one request per chunk of 1000. A failed request raises immediately; chunks already sent stay stored. Payload dicts built by hand (`ObservationPayload`) are accepted too.

```python
from flythings import Observation, Series

temperature = Series("<device>", "<sensor>", "temperature")

client.insertion_api().send_observations([Observation(temperature, 21.5, ts), Observation(temperature, 19.0, ts2)])
```

## Methods

| Method | Description |
| --- | --- |
| `send_observations(observations)` | Sends many observations (`/observation/multiple`). |
| `send_predictions(predictions)` | Sends many predictions (`/prediction/multiple`). Predictions are `Observation` objects too. |
| `send_observation(observation)` | Sends one observation (`/observation/single`). |
| `send_prediction(prediction)` | Sends one prediction (`/prediction/single`). |
| `send_record(series_id, observations)` | Sends a record to a series by ID. A string is sent as is; anything else as JSON. Returns the server's response. |
| `send_observations_csv(lines)` | Sends CSV lines built with `Observation.to_csv()` or `csv_line()`. A string, bytes or an open file (text or binary) is sent as is, as in 2.x; any other iterable is sent one line per item, with each item's line ending removed. Returns the server's response. |
| `register_device(name, *, device_type=None, geom=None, always_update=False)` | Creates the device on the server once per server, unless `always_update=True`. As in 2.x, registered devices are recorded in the client's `foi_cache` file (`.foiCache` by default), so later runs sharing that file do not register them again. `device_type` is applied only when the server knows it. The device is remembered only after the server accepts it, so a failed registration can be retried. Returns whether a request was sent. |

## Example

```python
import time

from flythings import Observation

now = int(time.time() * 1000)
temperature = client.series("temperature")  # default device and sensor

insertion = client.insertion_api()
insertion.register_device("<device>", geom={"type": "Point", "crs": "4326", "coordinates": [-8.4, 43.3]})
insertion.send_observations([Observation(temperature, 20 + i, now - i * 60_000, uom="C") for i in range(60)])
insertion.send_predictions([Observation(temperature, 22.0, now + 3_600_000)])
insertion.send_observation(Observation.from_file(temperature, "photo.png", time=now))
```
