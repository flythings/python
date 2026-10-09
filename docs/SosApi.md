# SosApi

[Back to the README](../README.md) · [Client, connections and series](Client.md)

Device metadata and infrastructures (feature tags). Get it with `client.sos_api()`.

## Methods

| Method | Description |
| --- | --- |
| `save_text_metadata(key, value, foi=None)` | Saves a text metadata entry on a device (the client's device by default). Keys are upper-cased. |
| `save_date_metadata(key, value, foi=None)` | The same for a date. |
| `save_infrastructure(infrastructure, infrastructure_id=None)` | Creates or updates an infrastructure with its metadata and devices. Returns the server's response. |
| `save_infrastructure_with_metadata(infrastructure, infrastructure_id=None)` | Same request as `save_infrastructure`, kept for 2.x callers. |
| `save_infrastructure_without_override_fois(infrastructure, infrastructure_id=None)` | Creates or updates an infrastructure without replacing its device list. |
| `link_device_to_infrastructure(infrastructure_tree, foi_identifier)` | Links a device to an infrastructure tree. |

The `infrastructure` argument is not modified; the ID is set on a copy.

## Builders

| Function | Description |
| --- | --- |
| `infrastructure(name, type, geom=None, geom_type=None, fois=None, alias=None, text_metadata=None)` | Builds an `Infrastructure` document. `text_metadata` is sent whenever it is not `None`, even as an empty list, as in 2.x. `geom_type` is a `SamplingFeatureType` (`POINT`, `LINE`, `POLYGON`, `NO_POSITION`, the default). |
| `text_metadata(key, value, tag_id=None)` | Builds a `Metadata` entry for `infrastructure(text_metadata=[...])`. |

## Example

```python
from flythings import SamplingFeatureType, infrastructure, text_metadata

plant = infrastructure(
    "<name>",
    "<type>",
    geom={"type": "Point", "crs": "4326", "coordinates": [-8.4, 43.3]},
    geom_type=SamplingFeatureType.POINT,
    fois=["<device>"],
    text_metadata=[text_metadata("site", "<site>")],
)
saved = client.sos_api().save_infrastructure(plant)
```
