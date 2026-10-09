# QueryApi

[Back to the README](../README.md) · [Client, connections and series](Client.md)

Searches observations and predictions, and looks up series. Get it with `client.query_api()`.

## Searching several series

`search_observations` and `search_predictions` search every series in one request. Each result is a flat `Row` dict, `{"foi", "procedure", "observable_property", "time", "value"}`, with the same names as the `Series` fields, so the results load straight into pandas.

```python
import pandas

from flythings import Series

rows = client.query_api().search_observations(
    [Series("dev1", "sensor", "temperature"), Series("dev2", "sensor", "power")],
    start=start_ms,
    end=end_ms,
    aggregation="HOURLY",
    aggregation_type="MEAN",
)
for row in rows:
    print(row["foi"], row["observable_property"], row["time"], row["value"])

# With pandas: one column per device and property
df = pandas.DataFrame(rows)
wide = df.pivot_table(index="time", columns=["foi", "observable_property"], values="value")
```

Without dates, the last week is searched; otherwise `end` defaults to now and a missing `start` is sent empty. Both take epoch milliseconds or a `datetime`. Duplicated series are searched once. Two series may not differ only in `as_incremental`, because results are matched on device, sensor and property.

| Parameter | Values |
| --- | --- |
| `aggregation` | `HOURLY`, `HOUR_OF_DAY`, `DAILY`, `DAY_OF_WEEK`, `MONTHLY`, `DAY_OF_MONTH`, `ANNUALLY`, `MONTH_OF_YEAR` |
| `aggregation_type` | `MIN`, `MAX`, `MEAN`, `SUM`, `LAST`, `FIRST`, `COUNT`, `STD` |

## Methods

| Method | Description |
| --- | --- |
| `search_observations(series, start=None, end=None, *, aggregation=None, aggregation_type=None)` | Observations of several series, as a list of `Row` dicts. |
| `search_predictions(series, start=None, end=None, *, aggregation=None, aggregation_type=None)` | The same for predictions. |
| `search_by_id(series_id, start=None, end=None, *, as_incremental=False, aggregation=None, aggregation_type=None)` | Observations of one series by ID, as a list of `Point` dicts, `{"value", "time"}`: the shape 2.x `search` returned, keys in the same order. |
| `search_predictions_by_id(...)` | The same for predictions. |
| `find_series(series)` | The series description (`FoundSeries`, with its `id`), or `None` when it does not exist (the server answers 400 or 404). |
| `get_last_observation_before_date(series_id, timestamp)` | The last value before `timestamp` as `{"time", "value"}`. Returns `None` when there is none or the server answers anything but 200; rejected credentials (401/403) still raise `AuthenticationError`. |
