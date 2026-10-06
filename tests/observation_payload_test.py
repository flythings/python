from flythings import InsertionModule


def test_get_observation_defaults_to_config_device_and_sensor(config):
    client = InsertionModule(config)
    assert client.get_observation(20, "temperature") == {
        "observableProperty": "temperature",
        "value": 20,
        "procedure": "sensor",
        "foi": "device",
    }


def test_get_observation_with_all_fields(config):
    client = InsertionModule(config)
    observation = client.get_observation(
        20,
        "temperature",
        uom="C",
        ts=1700000000000,
        geom={"type": "Point", "coordinates": [0, 0]},
        procedure="proc",
        foi="foi",
        device_type="type",
        foi_name="name",
        force_type="NUMBER",
    )
    assert observation["uom"] == "C"
    assert observation["time"] == 1700000000000
    assert observation["procedure"] == "proc"
    assert observation["foi"] == "foi"
    assert observation["deviceType"] == "type"
    assert observation["foiName"] == "name"
    assert observation["forceType"] == "NUMBER"
