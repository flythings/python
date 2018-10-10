#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import time
import socket
from datetime import timedelta, datetime

PUBLISH_MULTIPLE_URL = '/observation/multiple'
GET_OBSERVATIONS_URL = '/observation'
PUBLISH_SINGLE_URL = '/observation/single'
LOGIN_DEVICE_URL = '/login/device'
LOGIN_USER_URL = '/login/'
SOKET_URL = '/socket'
SERIES_URL = '/series/'
FILE = 'Configuration.properties'

headers = {'x-auth-token': '', 'Content-Type': 'application/json'}

clientSocket = None

gFoi = ''
gProcedure = ''
gServer = ''
gUser = ''
gPassword = ''
gHash = ''
gWorkspace = ''
gTimeout = 1000


def login(user, password, login_type):
    try:
        if login_type == 'DEVICE':
            authbody = requests.get('http://' + gServer + LOGIN_DEVICE_URL, auth=(user, password), timeout=10)
        elif login_type == 'USER':
            authbody = requests.get('http://' + gServer + LOGIN_USER_URL, auth=(user, password), timeout=10)
        else:
            return "Error: login_type not valid"
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

def setTiemout(timeout):
    global gTimeout
    gTimeout = timeout
    return gTimeout


def sendObservations(values):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    response = requests.put('http://' + gServer + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}, timeout=gTimeout),
                            headers=headers)
    return response.status_code


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


def __connectSocket():
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None

    decode = lambda d: d.decode('utf-8')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ":" not in gServer:
            server = gServer
        else:
            server = gServer.split(":")[0]

        response = requests.get('http://' + gServer + SOKET_URL, headers=headers, timeout=gTimeout)
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


def sendSocket(seriesId, value, timestamp):
    global clientSocket
    if clientSocket is None:
        clientSocket = __connectSocket()
    if clientSocket is not None:
        jsonPayload = json.dumps({
            'seriesId': seriesId,
            'timestamp': timestamp,
            'value': value
        })
        try:
            clientSocket.sendall((jsonPayload + "\n").encode("utf-8"))
        except socket.error as msg:
            clientSocket.close()
            clientSocket = None
            print(msg)
    else:
        print("ERROR CONNECTING TO SOCKET")


__loadAuthData()
