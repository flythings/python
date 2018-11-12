import flythings
import time
import random
from flythings import ActionDataTypes
flythings.loadDataByFile('Configuration.properties')
# Server, user and password are specified in the configuration File, if you dont have it, create the Configuration.properties file and specify those fields.
def sendObservation_test():
    x = flythings.sendObservation(20, 'op', 'uoms', None, None, 'procedure', 'foi')
    assert str(x) == str(b'{"message":"Full insertion","type":"Ok"}')


def sendObservations_test():
    observations = [flythings.getObservation(20, "test1", None, None, None, "ob1", "multiple"),
                    flythings.getObservation(30, "test2", None, None, None, "ob1", "multiple"),
                    flythings.getObservation(40, "test3", None, None, None, "ob1", "multiple"),
                    flythings.getObservation(50, "test4", "uoms", round(time.time() * 1000), None, "ob1", "multiple")]
    x = flythings.sendObservations(observations)
    assert str(x) == str('{"message":"Full insertion","type":"Ok"}')


def search_test():
    x = flythings.search(947, 1495643746000, 1496248546000)
    assert str(x[1]['time']) == '1496218547000'
    assert str(x[1]['value']) == '20.0'


def user_login():
	flythings.setServer('<Put the server here>')
	flythings.setWorkspace('<Put the workspace here>')
	flythings.login('<Put the user here>', '<Put the password here>', 'DEVICE')

def socket_test():
    i = 0
    while i < 100:
        flythings.sendSocket(51, random.random() * 10, int(time.time() * 1000))
        flythings.sendSocket(47, random.random() * 15, int(time.time() * 1000))
        i += 1
        time.sleep(2)


def find_series():
    return flythings.findSeries("Raspberry Pi", "System", "Free Memory")

def register_action():
    flythings.setDevice("vagrant")
    flythings.setSensor("process")

    def test(param):
        if param:
            print("test function true")
        else:
            print("test function false")
        return "OK"

    result = flythings.registerAction("testAction", test, parameterType=ActionDataTypes.ARRAY)
    result2 = flythings.registerActionForSeries("testAction2", "proc_status", "", test, parameterType=ActionDataTypes.BOOLEAN)
    return result and result2


def test_action():
    flythings.setDevice("vagrant")
    flythings.setSensor("system")

    def test(param):
        print(param)
        return 0

    result = flythings.registerAction("FileAction", test, parameterType=ActionDataTypes.FILE)
    result2 = flythings.registerActionForSeries("BooleanAction", "proc_status", "", test, parameterType=ActionDataTypes.BOOLEAN, procedure="process")
    result3 = flythings.registerActionForSeries("NumberAction", "disk_ocupation", "", test, parameterType=ActionDataTypes.NUMBER)
    result4 = flythings.registerActionForSeries("ArrayAction", "memory_usage", "", test, parameterType=ActionDataTypes.ARRAY)
    result5 = flythings.registerActionForSeries("TextAction", "cpu_2_usage", "", test, parameterType=ActionDataTypes.TEXT)
    return result and result2 and result3 and result4 and result5


def start_action():
    if test_action():
        print("starting thread...")
        flythings.startActionListening()
        time.sleep(10)
        print("stoping thread...")
        flythings.stopActionListening()

user_login()
sendObservation_test()
sendObservations_test()
search_test()
#socket_test()
find_series()
# register_action()
# start_action()
