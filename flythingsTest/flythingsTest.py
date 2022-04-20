import flythings
import time
import random
from flythings import ActionDataTypes
flythings.load_data_by_file('Configuration.properties')
# Server, user and password are specified in the configuration File, if you dont have it, create the Configuration.properties file and specify those fields.
def sendObservation_test():
    x = flythings.send_observation(20, 'op', 'uoms', None, None, 'procedure', 'foi')
    assert str(x) == str(b'{"message":"Full insertion","type":"Ok"}')


def sendObservations_test():
    observations = [flythings.get_observation(20, "test1", None, None, None, "ob1", "multiple"),
                    flythings.get_observation(30, "test2", None, None, None, "ob1", "multiple"),
                    flythings.get_observation(40, "test3", None, None, None, "ob1", "multiple"),
                    flythings.get_observation(50, "test4", "uoms", round(time.time() * 1000), None, "ob1", "multiple")]
    x = flythings.send_observations(observations)
    assert str(x) == str('200')


def search_test():
    x = flythings.search(947, 1495643746000, 1496248546000)
    assert str(x[1]['time']) == '1496218547000'
    assert str(x[1]['value']) == '20.0'


def user_login():
	flythings.set_server('<Put the server here>')
	flythings.set_workspace('<Put the workspace here>')
	flythings.login('<Put the user here>', '<Put the password here>', 'DEVICE')

def socket_test():
    i = 0
    while i < 100:
        flythings.send_socket(51, random.random() * 10, int(time.time() * 1000))
        flythings.send_socket(47, random.random() * 15, int(time.time() * 1000))
        i += 1
        time.sleep(2)


def find_series():
    return flythings.find_series("Raspberry Pi", "System", "Free Memory")

def register_action():
    flythings.set_device("vagrant")
    flythings.set_sensor("process")

    def test(param):
        if param:
            print("test function true")
        else:
            print("test function false")
        return 0

    result = flythings.register_action("testAction", test, parameter_type=ActionDataTypes.ARRAY)
    result2 = flythings.register_action_for_series("testAction2", "proc_status", "", test, parameter_type=ActionDataTypes.BOOLEAN)
    return result and result2


def test_action():
    flythings.set_device("vagrant")
    flythings.set_sensor("system")

    def test(param):
        print(param)
        return 0

    result = flythings.register_action("FileAction", test, parameter_type=ActionDataTypes.FILE)
    result2 = flythings.register_action_for_series("BooleanAction", "proc_status", "", test, parameter_type=ActionDataTypes.BOOLEAN, procedure="process")
    result3 = flythings.register_action_for_series("NumberAction", "disk_ocupation", "", test, parameter_type=ActionDataTypes.NUMBER)
    result4 = flythings.register_action_for_series("ArrayAction", "memory_usage", "", test, parameter_type=ActionDataTypes.ARRAY)
    result5 = flythings.register_action_for_series("TextAction", "cpu_2_usage", "", test, parameter_type=ActionDataTypes.TEXT)
    return result and result2 and result3 and result4 and result5


def start_action():
    if test_action():
        print("starting thread...")
        flythings.start_action_listening()
        time.sleep(10)
        print("stoping thread...")
        flythings.stop_action_listening()

user_login()
sendObservation_test()
sendObservations_test()
search_test()
#socket_test()
find_series()
# register_action()
# start_action()
