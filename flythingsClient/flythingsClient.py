import json, requests
import random
from datetime import timedelta, date


PUBLISH_MULTIPLE_URL = '/firefly/observation/multiple'
GET_OBSERVATIONS_URL = '/firefly/observation'
PUBLISH_SINGLE_URL = '/firefly/observation/single'
LOGIN_URL = '/firefly/login/device'
FILE = 'Configuration.properties'

headers = {'x-auth-token': '',
           'Content-Type': 'application/json'}

gFoi =''
gProcedure = ''
gServer = ''
gUser = ''
gPassword = ''
gHash= ''



def __loadAuthData():
	for line in open(FILE):
		text = line.strip()
		text = text.replace("\n", "")
		list = text.split(':')
		if (len(list) > 1):
			if (list[0].lower() == 'token'):
				list[1] = list[1].strip()
				global headers
				headers['x-auth-token'] = list[1]
			elif (list[0].lower() == 'server'):
				list[1] = list[1].strip()
				global gServer
				gServer =  list[1]
			elif (list[0].lower() == 'user'):
				list[1] = list[1].strip()
				global gUser
				gUser =  list[1]
			elif (list[0].lower() == 'password'):
				list[1] = list[1].strip()
				global gPassword
				gPassword =  list[1]
			elif (list[0].lower() == 'token'):
				list[1] = list[1].strip()
				global gToken
				gToken =  list[1]
			elif (list[0].lower() == 'hash'):
				list[1] = list[1].strip()
				gHash
				gHash =  list[1]
			elif (list[0].lower() == 'device'):
				list[1] = list[1].strip()
				global gFoi
				gFoi =  list[1]
			elif (list[0].lower() == 'sensor'):
				list[1] = list[1].strip()
				global gProcedure
				gProcedure =  list[1]
		if(gUser!='' and gPassword!=''):
			login(gUser,gPassword)


def login(user,password):
	authbody = requests.get('http://'+gServer+LOGIN_URL, auth=(user, password))
	global headers
	if(authbody.status_code==200):
		headers['x-auth-token'] = str(json.loads(authbody.text)['token'])
	else:
		print authbody.text
		raise


def setServer(server):
	global gServer
	gServer = server

def setDevice(device):
	global gFoi
	gFoi = device

def	setSensor(sensor):
	global gProcedure
	gProcedure = sensor

def setToken(token):
	global headers
	headers['x-auth-token'] = token

def sendObservations(values):
	if(headers['x-auth-token']==''):
		print 'NoAuthenticationError'
		raise
	r = requests.put('http://'+gServer+PUBLISH_MULTIPLE_URL,data=json.dumps({'observations': values}),headers = headers)
	if(r.status_code == 200):
		print(r.text)
	else:
		return r.text


def search(series,start_date,end_date,aggrupation=None,aggrupationType=None):
	if(headers['x-auth-token']==''):
		print 'NoAuthenticationError'
		raise
	message = {}
	serieArray = []
	serie = {}
	serie['id'] = series
	serieArray.append(serie)
	message['series'] = serieArray
	message['startDate'] = start_date
	message['endDate'] = end_date
	if(aggrupation!=None):
		message['temporalScale'] = aggrupation
	if(aggrupationType!=None):
		message['temporalScaleType'] = aggrupationType
	r = requests.post('http://'+gServer+GET_OBSERVATIONS_URL,data = json.dumps(message),headers = headers)
	if(r.status_code==200):
		list = r.json()[0]['data']
		returnList = []
		for elem in list:
			returnList.append({'value': elem[1], 'time': elem[0]})
		return returnList

	else:
		print r.text

def sendObservation(value,property,uom=None, time=None, geom=None, procedure=None, foi=None):
	if (headers['x-auth-token'] == ''):
		print 'NoAuthenticationError'
		raise
	message = getObservation(value,property,uom, time, geom, procedure, foi)
	json_payload = json.dumps(message)
	response = requests.put('http://'+gServer+PUBLISH_SINGLE_URL, json_payload,headers=headers)
	print(response.content)

def getObservation(value,property,uom=None, time=None, geom=None, procedure=None, foi=None):
	message = {}
	message['observableProperty'] = property
	message['value'] = str(value)
	if(uom!=None):
		message['uom'] = uom
	if(time!=None):
		message['time'] = time
	if(geom!=None):
		message['geom'] = geom
	if(procedure!=None):
		message['procedure'] = procedure
	else:
		message['procedure'] = gProcedure
	if(foi!=None):
		message['foi'] = foi
	else:
		message['foi'] = gFoi

	return message

__loadAuthData()