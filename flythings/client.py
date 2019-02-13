#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import time
import socket
from datetime import timedelta, datetime
from threading import Thread, Event, Lock
from enum import Enum
import ast
import copy
import os
import sys

PUBLISH_MULTIPLE_URL = '/observation/multiple'
GET_OBSERVATIONS_URL = '/observation'
PUBLISH_SINGLE_URL = '/observation/single'
PUBLISH_RECORD_URL = '/observation/record'
PUBLISH_PLAIN_CSV_URL = '/observation/csv/nofile'
FOI_URL = '/featureofinterest'
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
gRealTimeAcumulator = {}
gBatchEnabled = False
gBatchTimeout = 50
gRealTimeTimeout = 1400
gLastRealTimeTimestamp = None


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
            login_type = 'USER'
            authbody = requests.get('http://' + gServer + LOGIN_USER_URL, auth=(user, password), timeout=gTimeout)
        if authbody.status_code == 200:
            global headers
            body = json.loads(authbody.text)
            headers['x-auth-token'] = str(body['token'])
            if login_type == 'USER' and 'workspace' in body:
                headers['Workspace'] = str(body['workspace'])
            else:
                headers['Workspace'] = str(gWorkspace)
        else:
            print('ERROR AUTHENTICATED, CHECK THE USER OR PASSWORD')
            return None
    except requests.exceptions.InvalidURL:
        print('INVALID SERVER')
        raise


def loadDataByFile(file=None):
    if (file == None):
        file = FILE
    global gServer
    try:
        for line in open(file):
            text = line.strip().replace('\n', '')
            list_param = text.split(':')
            __update_file_params(list_param)
        if gUser != '' and gPassword != '':
            login(gUser, gPassword, g_login_type)
        global gServer
        if gServer == '':
            gServer = 'api.flythings.io'
        print('Succesfully loaded data from file ' + file)
    except Exception:
        print('CONFIGURATION FILE, ' + file + ' DONT EXIST, YOU MUST INSERT THE PARAMETERS MANUALLY')


def __update_file_params(list_param):
    if len(list_param) > 1:
        if list_param[0].lower() == 'token':
            list_param[1] = list_param[1].strip()
            global headers
            global gToken
            gToken = list_param[1]
            headers['x-auth-token'] = list_param[1]
        elif list_param[0].lower() == 'server':
            global gServer
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


def setServer(server):
    global gServer
    gServer = server
    return gServer


def __update_foi_file():
    file = open(".foiCache", "r")
    for line in file:
        line_items = line.split('\t')
        if (line_items[0] == gServer and line_items[1] == gFoi):
            return False
    file.close()
    file = open('.foiCache', 'a')
    file.write(gServer + '\t' + gFoi + '\t' + '\n')
    file.close()
    return True


def setDevice(device, object=None):
    global gFoi
    gFoi = device
    foi_to_send = {}
    foi_to_send['featureOfInterest'] = {"name": device}
    if (object != None):
        if ('type' in object):
            response = requests.get('http://' + gServer + FOI_URL + '/devicetypes', headers=headers, timeout=gTimeout)
            if (response.status_code == 200):
                device_types = response.json()
                if (object['type'] in device_types):
                    foi_to_send['device'] = object['type']
            else:
                print(str(response.status_code) + "FAIL RETRIEVING DEVICE TYPES")
        if ('geom' in object):
            foi_to_send['featureOfInterest']['geom'] = object['geom']
    if (__update_foi_file()):
        requests.post('http://' + gServer + FOI_URL, json.dumps(foi_to_send), headers=headers,
                      timeout=gTimeout)
    return gFoi


def setCustomHeader(header, header_value):
    global headers
    headers[header] = header_value
    return headers[header]


def getHeaders():
    global headers
    return headers


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


def setBatchEnabled(batchEnabled):
    global gBatchEnabled
    global thread
    gBatchEnabled = batchEnabled
    if (gBatchEnabled):
        if (not thread.is_alive()):
            thread.start()
    else:
        if (thread.is_alive()):
            thread.join()
    return gBatchEnabled


def sendObservations(values):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    response = requests.put('http://' + gServer + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}),
                            headers=headers, timeout=gTimeout)
    return response.status_code


def sendRecord(serie_id, json):
    if (headers['x-auth-token'] == ''):
        print('NoAuthenticationError')
        return None
    response = requests.put('http://' + gServer + PUBLISH_RECORD_URL + "/" + str(serie_id), json, headers=headers)
    return response.status_code, response.content


def sendObservationsCSV(values):
    if (headers['x-auth-token'] == ''):
        print('NoAuthenticationError')
        return None
    response = requests.post('http://' + gServer + PUBLISH_PLAIN_CSV_URL, data=values, headers=headers,
                             timeout=gTimeout)
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
        aux_time = datetime.today() - timedelta(weeks=1)
        start_date = round(aux_time.timestamp() * 1000)
    elif end_date is None:
        end_date = round(time.time() * 1000)

    message = {'series': [{'id': series, 'asIncremental': as_incremental}], 'startDate': start_date,
               'endDate': end_date}

    if aggrupation is not None:
        message['temporalScale'] = aggrupation
    if aggrupationType is not None:
        message['temporalScaleType'] = aggrupationType
    r = requests.post('http://' + gServer + GET_OBSERVATIONS_URL, data=json.dumps(message), headers=headers,
                      timeout=gTimeout)
    if r.status_code == 200:
        list = r.json()[0]['data']
        return_list = []
        for elem in list:
            return_list.append({'value': elem[1], 'time': elem[0]})
        return return_list
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
    if procedure is not None and procedure != '':
        message['procedure'] = procedure
    else:
        message['procedure'] = gProcedure
    if foi is not None and foi != '':
        message['foi'] = foi
    else:
        message['foi'] = gFoi

    return message


def getObservationCSV(
        value,
        series=None,
        uom=None,
        ts=None,
        property=None,
        procedure=None,
        foi=None,
):
    message = ''
    if series is not None:
        message += str(series) + ";"
    else:
        if foi is not None:
            message += foi + ";"
        else:
            message += gFoi + ";"
        if procedure is not None:
            message += procedure + ";"
        else:
            message += gProcedure + ";"
        if property is not None:
            message += property + ";"
        else:
            return None
    if ts is not None:
        message += str(ts)
    else:
        message += str(int(time.time() * 1000))
    if uom is not None:
        message += ";" + uom
    return message


def findSeries(foi=None, procedure=None, observable_property=None):
    if foi is None or foi == '':
        foi = gFoi
    if procedure is None or procedure == '':
        procedure = gProcedure
    if observable_property is None or observable_property == '':
        return "INSERT A OBSERVABLE PROPERTY"
    response = requests.get('http://' + gServer + SERIES_URL + foi + '/' + procedure + '/' + observable_property,
                            headers=headers, timeout=gTimeout)
    message = json.loads(response.text)
    if response.status_code != 200:
        print("Error retrieving series: " + foi + "-" + procedure + "-" + observable_property)
        return None
    return message


def __get_tcp_socket(url=None):
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
                is_logged = s.recv(1024)
                if decode(is_logged) == 'True':
                    return s
                else:
                    print("INVALID_TOKEN")
            else:
                print("SOCKET UNAVAILABLE!")
    except:
        print("Connection refused")
    return None


def __get_udp_socket():
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


def __get_socket(protocol):
    if protocol is None or protocol.upper() == "TCP":
        global clientTCPSocket
        if clientTCPSocket is None:
            clientTCPSocket = __get_tcp_socket()
            clientTCPSocket.settimeout(15.0)
        return clientTCPSocket
    else:
        global clientUDPSocket
        if clientTCPSocket is None:
            clientUDPSocket = __get_udp_socket()
        return clientUDPSocket


def __get_payload(series_id, value, timestamp, protocol):
    if (protocol is None or protocol.upper() == "TCP"):
        return json.dumps({
            'seriesId': series_id,
            'timestamp': timestamp,
            'value': value
        }) + "\n"
    else:
        return json.dumps({
            'X-AUTH-TOKEN': headers['x-auth-token'],
            'data': {
                'seriesId': series_id,
                'timestamp': timestamp,
                'value': value
            }
        })


def __reset_socket(protocol):
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


def sendSocket(series_id, value, timestamp, protocol=None):
    if (gBatchEnabled):
        lock.acquire()
        global gRealTimeAcumulator
        global gBatchTimeout
        if str(series_id) in gRealTimeAcumulator:
            if int(time.time() * 1000) - \
                    gRealTimeAcumulator[str(series_id)][len(gRealTimeAcumulator[str(series_id)]) - 1][
                        'timestamp'] >= gBatchTimeout:
                gRealTimeAcumulator[str(series_id)].append({
                    'seriesId': series_id,
                    'timestamp': timestamp,
                    'value': value
                })
            else:
                lock.release()
                e_message = 'ERROR, DEVICE MUST WAIT AT LEAST 50ms BEFORE ACUMULATE ANOTHER OBSERVATION'
                print(e_message, flush=True)
                return e_message
        else:
            gRealTimeAcumulator[str(series_id)] = [{
                'seriesId': series_id,
                'timestamp': timestamp,
                'value': value
            }]
        lock.release()
    else:
        global gLastRealTimeTimestamp
        if gLastRealTimeTimestamp == None or int(time.time() * 1000) - gLastRealTimeTimestamp >= gRealTimeTimeout:
            clientSocket = __get_socket(protocol)

            if clientSocket is not None:
                json_payload = __get_payload(series_id, value, timestamp, protocol)
                try:
                    clientSocket.sendall(json_payload.encode("utf-8"))
                except socket.error as msg:
                    __reset_socket(protocol)
                    print(msg)
            else:
                print("ERROR CONNECTING TO SOCKET")
            print('CORRECT SENDED')
            gLastRealTimeTimestamp = int(time.time() * 1000)
        else:
            e_message = 'ERROR, DEVICE MUST WAIT AT LEAST 1400ms BEFORE SEND A OBSERVATION FROM REALTIME'
            print(e_message)
            return e_message


def __acumulator_series_to_json(data):
    return json.dumps({'seriesId': data[0]['seriesId'],
                       'obs': sorted(data, key=lambda o: o['timestamp'])
                       }) + "\n"


def __send_socket_batch(protocol=None):
    while (True):
        global gBatchEnabled
        if (gBatchEnabled):
            clientSocket = __get_socket(protocol)
            lock.acquire()
            global gRealTimeAcumulator
            acumulator = copy.deepcopy(gRealTimeAcumulator)
            if clientSocket is not None:
                gRealTimeAcumulator = {}
                lock.release()
                try:
                    values = acumulator.values()
                    for value in values:
                        json_payload = __acumulator_series_to_json(value)
                        clientSocket.sendall(json_payload.encode("utf-8"))
                except (socket.error, socket.timeout) as msg:
                    print("SOCKET ERROR:" + str(msg), flush=True)
                    __reset_socket(protocol)
            else:
                lock.release()
                print("ERROR CONNECTING TO SOCKET", flush=True)
        time.sleep(5)


def __register_action(
        name,
        parameter_type=None,
        foi=None,
        procedure=None,
        observable_property=None,
        unit=None,
        alias=None
):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    elif foi is None and gFoi is None:
        print('NoDeviceError')
        return None
    elif observable_property is not None and (gProcedure is None and procedure is None):
        print('NoProcedureError')
        return None
    try:
        payload = {
            "name": name,
            "featureOfInterest": gFoi if foi is None else foi,
            "parameterType": ActionDataTypes(parameter_type).name if parameter_type is not None else None
        }
        if observable_property is not None:
            payload["procedure"] = gProcedure if procedure is None else procedure
            payload["observableProperty"] = observable_property
        if unit is not None:
            payload["unit"] = unit
        if alias is not None:
            payload["alias"] = alias
        response = requests.post('http://' + gServer + ACTIONS_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 201:
            return True
        else:
            print(response.status_code)
    except Exception as e:
        print(e)
    return None


def registerActionForSeries(name, observableProperty, unit, callback, foi=None, procedure=None, parameterType=None,
                            alias=None):
    result = __register_action(name, parameterType, foi, procedure, observableProperty, unit, alias=alias)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback': callback, 'parameterType': parameterType}
        else:
            return False
    return result is not None


def registerAction(name, callback, foi=None, parameterType=None, alias=None):
    result = __register_action(name, parameterType, foi, alias=alias)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback': callback, 'parameterType': parameterType}
        else:
            return False
    return result is not None


def __action_socket_client(actionThreadStop, callbacks, foi):
    actionSocket = None
    while not actionThreadStop.is_set():
        try:
            if actionSocket is None:
                actionSocket = __get_tcp_socket(ACTIONS_URL)
            actionSocket.settimeout(60.0)
            data = actionSocket.recv(1024)
            decodedData = data.decode("utf-8")
            if decodedData != '':
                __parse_decoded_data(decodedData, actionSocket, foi)
            else:
                try:
                    actionSocket.sendall("Ping".encode("utf-8"))
                except:
                    print("The server closed the connection!")
                    break
        except socket.timeout:
            print("timeout")
            time.sleep(60)
            __action_socket_client(actionThreadStop, callbacks, foi)
        except Exception as e:
            if (str(e) != "'@PING@'"):
                time.sleep(60)
                __action_socket_client(actionThreadStop, callbacks, foi)
    actionSocket.close()


def __parse_decoded_data(decoded_data, action_socket, foi):
    if decoded_data == "DEVICE":
        action_socket.sendall((foi + "\n").encode("utf-8"))
    else:
        if '@PING@' in decoded_data:
            command = decoded_data
        else:
            response = json.loads(decoded_data)
            param = None
            ts = response["timestamp"]
            command = response["name"]
            if 'action' in response:
                param = response["action"]
        if (callbacks[command] is not None):
            try:
                result = callbacks[command]['callback'](
                    __cast_parameter(param, callbacks[command]['parameterType']), ts)
                if result == 0 or isinstance(result, str):
                    action_socket.sendall((str(result).replace('\n', '') + '\n').encode("utf-8"))
                else:
                    action_socket.sendall()
            except:
                print("ERROR DOING ACTION")


def __cast_parameter(param, parameter_type):
    try:
        if parameter_type == None:
            return None
        elif parameter_type == ActionDataTypes.TEXT or parameter_type == ActionDataTypes.FILE:
            return param
        elif parameter_type == ActionDataTypes.ARRAY:
            return param.split(";")
        elif parameter_type == ActionDataTypes.BOOLEAN:
            return param.lower() == 'true'
        elif parameter_type == ActionDataTypes.NUMBER:
            return ast.literal_eval(param)  # Number
    except:
        return None


def startActionListening(foi=None):
    if foi is not None and foi != '':
        f = foi
    else:
        f = gFoi
    if f is None or f == '':
        print("NoDeviceException")
        return None
    if not callbacks:
        print("NoRegisteredActionExcetion")
        return None
    global actionThreadStop, clientActionThread
    actionThreadStop = Event()
    clientActionThread = Thread(target=__action_socket_client, args=(actionThreadStop, callbacks, f))
    clientActionThread.start()


def stopActionListening():
    global actionThreadStop, clientActionThread
    if actionThreadStop:
        actionThreadStop.set()
    clientActionThread = None


if not os.path.exists(".foiCache"):
    f = open(".foiCache", "a")
    f.close()

thread = Thread(target=__send_socket_batch)
lock = Lock()
