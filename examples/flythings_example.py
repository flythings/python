"""Walkthrough of the flythings API against a live server.

Fill in the placeholders (or examples/Configuration.properties) and run with `uv run examples/flythings_example.py`.
Never commit real credentials.
"""

import random
import time

from flythings import (
    ActionDataTypes,
    Connection,
    FlyThings,
    Observation,
    Series,
    WriteOptions,
    infrastructure,
    text_metadata,
)

SERVER = "<Put the server here>"
TOKEN = "<Put the authorization (bearer) token here>"
OTHER_SERVER = "<Put a second server here>"
OTHER_TOKEN = "<Put its authorization (bearer) token here>"


def send_observations(client: FlyThings) -> None:
    temperature = Series("<device>", "<sensor>", "temperature")
    now = int(time.time() * 1000)
    insertion = client.insertion_api()
    insertion.send_observation(Observation(temperature, 21.5, now, uom="C"))
    insertion.send_observations([Observation(temperature, 20 + i, now - i * 60_000) for i in range(10)])
    insertion.send_predictions([Observation(temperature, 25.0, now + 3_600_000)])


def send_to_two_servers(client: FlyThings) -> None:
    # One client per server
    power = Series("<device>", "<sensor>", "power")
    now = int(time.time() * 1000)
    client.insertion_api().send_observations([Observation(power, 1.0, now)])
    with FlyThings(Connection(OTHER_SERVER, OTHER_TOKEN)) as other:
        other.insertion_api().send_observations([Observation(power, 2.0, now)])


def search(client: FlyThings) -> None:
    temperature = Series("<device>", "<sensor>", "temperature")
    for row in client.query_api().search_observations([temperature]):  # last week by default
        print(row["observable_property"], row["time"], row["value"])
    found = client.query_api().find_series(temperature)
    if found is not None:
        print(client.query_api().get_last_observation_before_date(found["id"], int(time.time() * 1000)))


def realtime(client: FlyThings, series_id: int) -> None:
    with client.realtime_api(WriteOptions(batch=True)) as api:
        for _ in range(100):
            api.send(series_id, random.random() * 10, int(time.time() * 1000))
            time.sleep(0.1)
    # leaving the block flushes what is still queued


def actions(client: FlyThings) -> None:
    def reboot(param: bool) -> int:
        print("reboot requested:", param)
        return 0

    with client.actions_api(device="<device>") as api:
        api.register_action("Reboot", reboot, parameter_type=ActionDataTypes.BOOLEAN)
        api.start_listening()
        time.sleep(10)
    # leaving the block stops the listener thread


def sos(client: FlyThings) -> None:
    api = client.sos_api()
    api.save_text_metadata("owner", "<owner>", foi="<device>")
    plant = infrastructure("<name>", "<type>", fois=["<device>"], text_metadata=[text_metadata("site", "<site>")])
    print(api.save_infrastructure(plant))


def main() -> None:
    with FlyThings(Connection(SERVER, TOKEN)) as client:
        # or: FlyThings.from_config_file("examples/Configuration.properties")
        # or: FlyThings(Connection.login(SERVER, "<user>", "<password>"))
        send_observations(client)
        search(client)
        # send_to_two_servers(client)
        # realtime(client, series_id=0)
        # actions(client)
        # sos(client)


if __name__ == "__main__":
    main()
