import flythings
import time


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
	flythings.login('<Put the user here>', '<Put the password here>', 'USER')


user_login()
sendObservation_test()
sendObservations_test()
search_test()