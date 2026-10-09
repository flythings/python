# RealTimeApi

[Back to the README](../README.md) · [Client, connections and series](Client.md)

Sends values to series (by ID) through the platform's real-time sockets. Get it with `client.realtime_api(write_options=None)`.

## Methods

| Method | Description |
| --- | --- |
| `send(series_id, value, timestamp, protocol="TCP")` | Sends a value now, over TCP (the default) or UDP. `protocol` is case-insensitive; any other value raises `ValueError`, including `None`, which 2.x treated as TCP: omit the argument instead. With batching enabled, queues it instead. |
| `flush()` | Sends the queued values now. If sending fails (socket, network or HTTP error), the unsent values are queued again and the error is raised. |
| `close()` / `with` block | Stops the batch thread, sends what is still queued and closes the sockets. `FlyThings.close()` does this for every real-time API it created. Values still queued when the program exits without `close()` are sent from an exit hook, but call `close()` (or use `with`) so errors can be handled. |

`send` raises `RateLimitError` when called too often: direct sends must be 1400 ms apart, and a batched value is rejected when it is queued less than 50 ms after the timestamp of the last value queued for its series. As in 2.x, the batch interval is measured from that timestamp, not from when it was queued, so values with past timestamps (a backfill) can be queued back to back. A failed direct send does not count towards that interval, so it can be retried at once. Socket failures raise `SocketError`; the next call opens a new socket.

Batches are delivered at least once: if the connection drops after a batch is written but before the server acknowledges it, `flush()` queues the batch again and sends it on the next attempt, so the server may store those values twice.

## `WriteOptions`

| Field | Default | Description |
| --- | --- | --- |
| `batch` | `False` | Queue values and send them from a background thread. |
| `flush_interval` | `5.0` | Seconds between batch sends. |
| `batch_min_interval_ms` | `50` | Minimum time between the timestamp of the last queued value of a series and queuing the next one. |
| `realtime_min_interval_ms` | `1400` | Minimum time between two direct sends. |

## Example

```python
import time

from flythings import WriteOptions

with client.realtime_api(WriteOptions(batch=True)) as realtime:
    for _ in range(100):
        realtime.send(series_id, read_sensor(), int(time.time() * 1000))
        time.sleep(0.1)
# leaving the block sends what is still queued
```
