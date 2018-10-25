#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import time
import socket
from datetime import timedelta, datetime
from threading import Thread, Event
from enum import Enum
import ast

PUBLISH_MULTIPLE_URL = '/observation/multiple'
GET_OBSERVATIONS_URL = '/observation'
PUBLISH_SINGLE_URL = '/observation/single'
PUBLISH_RECORD_URL = '/observation/record'
LOGIN_DEVICE_URL = '/login/device'
LOGIN_USER_URL = '/login/'
SOCKET_URL = '/socket'
SERIES_URL = '/series/'
ACTIONS_URL = '/newaction/'
FILE = 'Configuration.properties'

headers = {'x-auth-token': '', 'Content-Type': 'application/json'}

clientTCPSocket = None
clientUDPSocket = None

clientActionThread = None
callbacks = {}
actionThreadStop = False

gFoi = ''
gProcedure = ''
gServer = ''
gUser = ''
gPassword = ''
gHash = ''
gWorkspace = ''
gTimeout = 1000

class ActionDataTypes(Enum):
    BOOLEAN = 1,
    FILE = 2,
    NUMBER = 3,
    TEXT = 4,
    ARRAY = 5

def login(user, password, login_type):
    try:
        if login_type == 'DEVICE':
            authbody = requests.get('http://' + gServer + LOGIN_DEVICE_URL, auth=(user, password), timeout=gTimeout)
        elif login_type == 'USER':
            authbody = requests.get('http://' + gServer + LOGIN_USER_URL, auth=(user, password), timeout=gTimeout)
        else:
            login_type='USER'
            authbody = requests.get('http://' + gServer + LOGIN_USER_URL, auth=(user, password), timeout=gTimeout)
        if authbody.status_code == 200:
            global headers
            body = json.loads(authbody.text)
            headers['x-auth-token'] = str(body['token'])
            if login_type == 'USER' and 'workspace' in body:
                headers['Workspace'] = str(body['workspace'])
            else:
                headers['Workspace'] = str(gWorkspace)
    except requests.exceptions.InvalidURL:
        print('INVALID SERVER')
        raise


def __loadAuthData():
    global gServer
    try:
        for line in open(FILE):
            text = line.strip().replace('\n', '')
            list_param = text.split(':')
            if len(list_param) > 1:
                if list_param[0].lower() == 'token':
                    list_param[1] = list_param[1].strip()
                    global headers
                    headers['x-auth-token'] = list_param[1]
                elif list_param[0].lower() == 'server':
                    list_param[1] = list_param[1].strip()
                    gServer = list_param[1]
                elif list_param[0].lower() == 'user':
                    list_param[1] = list_param[1].strip()
                    global gUser
                    gUser = list_param[1]
                elif list_param[0].lower() == 'password':
                    list_param[1] = list_param[1].strip()
                    global gPassword
                    gPassword = list_param[1]
                elif list_param[0].lower() == 'login_type':
                    list_param[1] = list_param[1].strip()
                    global g_login_type
                    g_login_type = list_param[1]
                elif list_param[0].lower() == 'token':
                    list_param[1] = list_param[1].strip()
                    global gToken
                    gToken = list_param[1]
                elif list_param[0].lower() == 'hash':
                    list_param[1] = list_param[1].strip()
                    global gHash
                    gHash = list_param[1]
                elif list_param[0].lower() == 'device':
                    list_param[1] = list_param[1].strip()
                    global gFoi
                    gFoi = list_param[1]
                elif list_param[0].lower() == 'sensor':
                    list_param[1] = list_param[1].strip()
                    global gProcedure
                    gProcedure = list_param[1]
                elif list_param[0].lower() == 'timeout':
                    list_param[1] = list_param[1].strip()
                    global gTimeout
                    gTimeout = list_param[1]
        if gUser != '' and gPassword != '':
            login(gUser, gPassword, g_login_type)
        if gServer == '':
            gServer = 'api.flythings.io'
    except Exception:
        print('CONFIGURATION FILE, Configuration.properties DONT EXIST, YOU MUST INSERT THE PARAMETERS MANUALLY')


def setServer(server):
    global gServer
    gServer = server
    return gServer


def setDevice(device):
    global gFoi
    gFoi = device
    return gFoi


def setCustomHeader(header, header_value):
    global headers
    headers[header] = header_value
    return headers[header]


def setSensor(sensor):
    global gProcedure
    gProcedure = sensor
    return gProcedure


def setToken(token):
    global headers
    headers['x-auth-token'] = token
    return headers['x-auth-token']


def setWorkspace(workspace):
    global gWorkspace
    gWorkspace = workspace
    return gWorkspace


def setTimeout(timeout):
    global gTimeout
    gTimeout = timeout
    return gTimeout


def sendObservations(values):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    response = requests.put('http://' + gServer + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}),
                            headers=headers, timeout=gTimeout)
    return response.status_code


def sendRecord(serieId, json):
	if (headers['x-auth-token'] == ''):
		print ('NoAuthenticationError')
		return None
	response = requests.put('http://'+gServer+PUBLISH_RECORD_URL+"/"+str(serieId), json, headers=headers)
	return response.status_code, response.content


def search(
        series,
        start_date=None,
        end_date=None,
        aggrupation=None,
        aggrupationType=None,
        as_incremental=False
):
    if headers['x-auth-token'] == '':
        return 'NoAuthenticationError'

    # Default datetime
    if start_date is None and end_date is None:
        end_date = round(time.time() * 1000)
        auxTime = datetime.today() - timedelta(weeks=1)
        start_date = round(auxTime.timestamp() * 1000)
    elif end_date is None:
        end_date = round(time.time() * 1000)

    message = {'series': [{'id': series, 'asIncremental': as_incremental}], 'startDate': start_date,
               'endDate': end_date}

    if aggrupation is not None:
        message['temporalScale'] = aggrupation
    if aggrupationType is not None:
        message['temporalScaleType'] = aggrupationType
    r = requests.post('http://' + gServer + GET_OBSERVATIONS_URL, data=json.dumps(message), headers=headers, timeout=gTimeout)
    if r.status_code == 200:
        list = r.json()[0]['data']
        returnList = []
        for elem in list:
            returnList.append({'value': elem[1], 'time': elem[0]})
        return returnList
    else:
        print(r.text)


def sendObservation(
        value,
        property,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    message = getObservation(value, property, uom, ts, geom, procedure, foi)
    json_payload = json.dumps(message)
    response = requests.put('http://' + gServer + PUBLISH_SINGLE_URL, json_payload, headers=headers, timeout=gTimeout)
    return response.status_code


def getObservation(
        value,
        property,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
):
    message = {'observableProperty': property, 'value': value}
    if uom is not None:
        message['uom'] = uom
    if ts is not None:
        message['time'] = ts
    if geom is not None:
        message['geom'] = geom
    if procedure is not None:
        message['procedure'] = procedure
    else:
        message['procedure'] = gProcedure
    if foi is not None:
        message['foi'] = foi
    else:
        message['foi'] = gFoi

    return message


def findSeries(foi, procedure, observable_property):
    response = requests.get('http://' + gServer + SERIES_URL + foi + '/' + procedure + '/' + observable_property, headers=headers, timeout=gTimeout)
    message = json.loads(response.text)
    if response.status_code != 200:
        print("Error retrieving series: " +foi+"-"+procedure+"-"+observable_property)
        return None
    return message


def __getTCPSocket(url=None):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None

    decode = lambda d: d.decode('utf-8')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ":" not in gServer:
            if "/" not in gServer:
                server = gServer
            else:
                server = gServer.split("/")[0]
        else:
            server = gServer.split(":")[0]

        response = requests.get('http://' + gServer + (SOCKET_URL if url is None else url), headers=headers)
        if response.status_code == 200:
            port = int(response.text)

            s.connect((server, port))

            data = s.recv(1024)

            if decode(data) == 'X-AUTH-TOKEN':
                s.sendall((headers['x-auth-token'] + "\n").encode("utf-8"))
                isLogged = s.recv(1024)
                if decode(isLogged) == 'True':
                    return s
                else:
                    print("INVALID_TOKEN")
            else:
                print("SOCKET UNAVAILABLE!")
    except:
        print("Connection refused")
    return None


def __getUDPSocket():
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if ":" not in gServer:
            if "/" not in gServer:
                server = gServer
            else:
                server = gServer.split("/")[0]
        else:
            server = gServer.split(":")[0]

        response = requests.get('http://' + gServer + SOCKET_URL, headers=headers)
        if response.status_code == 200:
            port = int(response.text)

            s.connect((server, port))
            return s
    except:
        print("Connection refused")
    return None


def __getSocket(protocol):
    if protocol is None or protocol.upper() == "TCP":
        global clientTCPSocket
        if clientTCPSocket is None:
            clientTCPSocket = __getTCPSocket()
        return clientTCPSocket
    else:
        global clientUDPSocket
        if clientTCPSocket is None:
            clientUDPSocket = __getUDPSocket()
        return clientUDPSocket


def __getPayload(seriesId, value, timestamp, protocol):
    if (protocol is None or protocol.upper() == "TCP"):
        return json.dumps({
            'seriesId': seriesId,
            'timestamp': timestamp,
            'value': value
        }) + "\n"
    else:
        return json.dumps({
            'X-AUTH-TOKEN': headers['x-auth-token'],
            'data': {
                'seriesId': seriesId,
                'timestamp': timestamp,
                'value': value
            }
        })


def __resetSocket(protocol):
    if (protocol is None or protocol.upper() == "TCP"):
        global clientTCPSocket
        if clientTCPSocket is not None:
            clientTCPSocket.close()
            clientTCPSocket = None
    else:
        global clientUDPSocket
        if clientUDPSocket is not None:
            clientUDPSocket.close()
            clientUDPSocket = None


def sendSocket(seriesId, value, timestamp, protocol=None):
    clientSocket = __getSocket(protocol)

    if clientSocket is not None:
        jsonPayload = __getPayload(seriesId, value, timestamp, protocol)
        try:
            clientSocket.sendall(jsonPayload.encode("utf-8"))
        except socket.error as msg:
            __resetSocket(protocol)
            print(msg)
    else:
        print("ERROR CONNECTING TO SOCKET")


def __registerAction(
        name,
        parameterType=None,
        foi=None,
        procedure=None,
        observableProperty=None,
        unit=None
):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    elif foi is None and gFoi is None:
        print('NoDeviceError')
        return None
    elif observableProperty is not None and (gProcedure is None and procedure is None):
        print('NoProcedureError')
        return None
    try:
        payload = {
            "name": name,
            "featureOfInterest": gFoi if foi is None else foi,
            "parameterType": ActionDataTypes(parameterType).name if parameterType is not None else None
        }
        if observableProperty is not None:
            payload["procedure"] = gProcedure if procedure is None else procedure
            payload["observableProperty"] = observableProperty
            payload["unit"] = unit

        response = requests.post('http://' + gServer + ACTIONS_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 201:
            return True
        else:
            print(response.status_code)
    except Exception as e:
        print(e)
    return None


def registerActionForSeries(name, observableProperty, unit, callback, foi=None, procedure=None, parameterType=None):
    result = __registerAction(name, parameterType, foi, procedure, observableProperty, unit)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback':callback, 'parameterType': parameterType}
        else:
            return False
    return result is not None


def registerAction(name, callback, foi=None, parameterType=None):
    result = __registerAction(name, parameterType, foi)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback':callback, 'parameterType': parameterType}
        else:
            return False
    return result is not None


def __actionSocketClient(actionThreadStop, callbacks):
    actionSocket = None
    while not actionThreadStop.is_set():
        try:
            if actionSocket is None:
                actionSocket = __getTCPSocket(ACTIONS_URL)
            actionSocket.settimeout(60.0)
            data = actionSocket.recv(1024)
            decodedData = data.decode("utf-8")
            if decodedData != '':
                if decodedData == "DEVICE":
                    actionSocket.sendall((gFoi + "\n").encode("utf-8"))
                else:
                    param = None
                    if ":;:" in decodedData:
                        command, param = decodedData.split(":;:")
                    else:
                        command = decodedData
                    if(callbacks[command] is not None):
                        result = callbacks[command]['callback'](__castParameter(param, callbacks[command]['parameterType']))
                        actionSocket.sendall((str(result)+'\n').encode("utf-8"))
            else:
                try:
                    actionSocket.sendall("Ping".encode("utf-8"))
                except:
                    print("The server closed the connection!")
                    break
        except socket.timeout:
            print("timeout")
        except Exception as e:
            pass
    actionSocket.close()


def __castParameter(param, parameterType):
    try:
        if parameterType == None:
            return None
        elif parameterType == ActionDataTypes.TEXT:
            return param
        elif parameterType == ActionDataTypes.FILE:
            return param
        elif parameterType == ActionDataTypes.ARRAY:
            return param.split(";")
        elif parameterType == ActionDataTypes.BOOLEAN:
            return param.lower() == 'true'
        elif parameterType == ActionDataTypes.NUMBER:
            return ast.literal_eval(param) # Number
    except:
        return None


def startActionListening():
    if gFoi is None:
        print("NoDeviceException")
        return None
    if not callbacks:
        print("NoRegisteredActionExcetion")
        return None
    global actionThreadStop, clientActionThread
    actionThreadStop = Event()
    clientActionThread = Thread(target=__actionSocketClient, args=(actionThreadStop, callbacks))
    clientActionThread.start()


def stopActionListening():
    global actionThreadStop, clientActionThread
    if actionThreadStop:
        actionThreadStop.set()
    clientActionThread = None


__loadAuthData()
