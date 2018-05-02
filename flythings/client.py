#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import time
from datetime import timedelta, datetime

PUBLISH_MULTIPLE_URL = '/observation/multiple'
GET_OBSERVATIONS_URL = '/observation'
PUBLISH_SINGLE_URL = '/observation/single'
LOGIN_DEVICE_URL = '/login/device'
LOGIN_USER_URL = '/login/'
FILE = 'Configuration.properties'

headers = {'x-auth-token': '', 'Content-Type': 'application/json'}

gFoi = ''
gProcedure = ''
gServer = ''
gUser = ''
gPassword = ''
gHash = ''
gWorkspace = ''


def login(user, password, login_type):
    try:
        if login_type == 'DEVICE':
            authbody = requests.get('http://' + gServer + LOGIN_DEVICE_URL, auth=(user, password))
        elif login_type == 'USER':
            authbody = requests.get('http://' + gServer + LOGIN_USER_URL, auth=(user, password))
        else:
            return "Error: login_type not valid"
        if authbody.status_code == 200:
            global headers
            headers['x-auth-token'] = str(json.loads(authbody.text)['token'])
            if login_type == 'USER' and json.loads(authbody.text)['workspace'] is not None:
                headers['Workspace'] = str(json.loads(authbody.text)['workspace'])
            else:
                headers['Workspace'] = gWorkspace
    except requests.exceptions.InvalidURL:
        print ('INVALID SERVER')
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


def sendObservations(values):
    if headers['x-auth-token'] == '':
        print ('NoAuthenticationError')
        return None
    r = requests.put('http://' + gServer + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}), headers=headers)
    return r.text


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

    message = {'series': [{'id': series, 'asIncremental': as_incremental}], 'startDate': start_date, 'endDate': end_date}

    if aggrupation is not None:
        message['temporalScale'] = aggrupation
    if aggrupationType is not None:
        message['temporalScaleType'] = aggrupationType
    r = requests.post('http://' + gServer + GET_OBSERVATIONS_URL, data=json.dumps(message), headers=headers)
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
        print ('NoAuthenticationError')
        return None
    message = getObservation(value, property, uom, ts, geom, procedure, foi)
    json_payload = json.dumps(message)
    response = requests.put('http://' + gServer + PUBLISH_SINGLE_URL, json_payload, headers=headers)
    return response.content


def getObservation(
        value,
        property,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
):
    message = {'observableProperty': property, 'value': str(value)}
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


__loadAuthData()

