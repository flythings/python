#!/usr/bin/python
import random
import time

from flythings import InsertionModule, PredictionModule, RealTimeModule, SosModule, UtilModule, ActionModule, \
    ServerConfig, ActionDataTypes, BaseClient

# Server, user and password are specified in ServerConfig dataclass
config =  ServerConfig(
    server='<Put the server here>',
    user='<Put the user here>',
    password='<Put the password here>',
    login_type='USER',
    foi='',
    authorization='<Put the authtoken here>',
    token='<Pun the token here>'
)

actionModule = ActionModule(config=config)
insertionModule = InsertionModule(config=config)
predictionModule = PredictionModule(config=config)
realTimeModule = RealTimeModule(config=config)
sosModule = SosModule(config=config)
utilModule = UtilModule(config=config)


def sendObservation_test(client: InsertionModule):
    x = client.send_observation(40, 'op', 'uoms', None, None, 'procedure', 'foi')
    print(x)
    #assert str(x) == str(b'{"message":"Full insertion","type":"Ok"}')


def sendObservations_test(client: InsertionModule):
    observations = [client.get_observation(20, "test1", None, None, None, "ob1", "multiple"),
                    client.get_observation(30, "test2", None, None, None, "ob1", "multiple"),
                    client.get_observation(40, "test3", None, None, None, "ob1", "multiple"),
                    client.get_observation(50, "test4", "uoms", round(time.time() * 1000), None, "ob1", "multiple")]
    x = client.send_observations(observations)
    assert str(x) == str('200')


def search_test(client: InsertionModule):
    x = client.search(2, 1747642438985, 1748247015667)
    assert str(x[1]['time']) == '1496218547000'
    assert str(x[1]['value']) == '20.0'


def user_login(client: BaseClient):
	client.set_server('<Put the server here>')
	client.set_workspace('<Put the workspace here>')
	client.login('<Put the user here>', '<Put the password here>', 'DEVICE')

def socket_test(client: RealTimeModule):
    i = 0
    while i < 100:
        client.send_socket(51, random.random() * 10, int(time.time() * 1000))
        client.send_socket(47, random.random() * 15, int(time.time() * 1000))
        i += 1
        time.sleep(2)

    print("finished")


def find_series(client: InsertionModule):
    return client.find_series("foi", "procedure", "op")

def register_action(client: ActionModule):
    client.set_device("vagrant")
    client.set_sensor("process")

    def test(param):
        if param:
            print("test function true")
        else:
            print("test function false")
        return 0

    result = client.register_action("testAction", test, parameter_type=ActionDataTypes.ARRAY)
    result2 = client.register_action_for_series("testAction2", "proc_status", "", test, parameter_type=ActionDataTypes.BOOLEAN)
    return result and result2


def test_action(client: ActionModule):
    client.set_device("vagrant")
    client.set_sensor("system")

    def test(param):
        print(param)
        return 0

    result = client.register_action("FileAction", test, parameter_type=ActionDataTypes.FILE)
    result2 = client.register_action_for_series("BooleanAction", "proc_status", "", test, parameter_type=ActionDataTypes.BOOLEAN, procedure="process")
    result3 = client.register_action_for_series("NumberAction", "disk_ocupation", "", test, parameter_type=ActionDataTypes.NUMBER)
    result4 = client.register_action_for_series("ArrayAction", "memory_usage", "", test, parameter_type=ActionDataTypes.ARRAY)
    result5 = client.register_action_for_series("TextAction", "cpu_2_usage", "", test, parameter_type=ActionDataTypes.TEXT)
    return result and result2 and result3 and result4 and result5


def start_action(client: ActionModule):
    if test_action(client):
        print("starting thread...")
        client.start_action_listening()
        time.sleep(10)
        print("stoping thread...")
        client.stop_action_listening()


# user_login(insertionModule)
sendObservation_test(insertionModule)
sendObservations_test(insertionModule)
search_test(insertionModule)
#socket_test(realtimeModule)
find_series(insertionModule)
# register_action(actionModule)
# start_action(actionModule)
