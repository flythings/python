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
from inspect import signature

HTTP_ = 'http://'
HTTPS_ = 'http://'

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
DEVICE_ALERT_URL = '/alerts/device/send'
DEVICE_METADATA_URL = '/featureofinterest/metadata'
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

gActionSocket = None


class ActionDataTypes(Enum):
    BOOLEAN = 'BOOLEAN'
    NUMBER = 'NUMBER'
    TEXT = 'TEXT'
    DATE = 'DATE'
    SELECTOR = 'SELECTOR'
    ARRAY = 'ARRAY'
    JSON = 'JSON'
    FILE = 'FILE'
    LIVE = 'LIVE'


def login(user, password, login_type):
    try:
        if login_type == 'DEVICE':
            authbody = requests.get(HTTP_ + gServer + LOGIN_DEVICE_URL, auth=(user, password), timeout=gTimeout)
        elif login_type == 'USER':
            authbody = requests.get(HTTP_ + gServer + LOGIN_USER_URL, auth=(user, password), timeout=gTimeout)
        else:
            login_type = 'USER'
            authbody = requests.get(HTTP_ + gServer + LOGIN_USER_URL, auth=(user, password), timeout=gTimeout)
        if authbody.status_code == 200:
            global headers
            body = json.loads(authbody.text)
            headers['x-auth-token'] = str(body['token'])
            if login_type == 'USER' and 'workspace' in body:
                headers['Workspace'] = str(body['workspace'])
            else:
                headers['Workspace'] = str(gWorkspace)
            return str(body['token'])

        else:
            print('ERROR AUTHENTICATED, CHECK THE USER OR PASSWORD')
            return None
    except requests.exceptions.InvalidURL:
        print('INVALID SERVER')
        raise


def loadDataByFile(file=None):
    if file is None:
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
        if line_items[0] == gServer and line_items[1] == gFoi:
            return False
    file.close()
    file = open('.foiCache', 'a')
    file.write(gServer + '\t' + gFoi + '\t' + '\n')
    file.close()
    return True


def setDevice(device, object=None, always_update=False):
    global gFoi
    gFoi = device
    foi_to_send = {'featureOfInterest': {"name": device}}
    if object is not None:
        if 'type' in object:
            response = requests.get(HTTP_ + gServer + FOI_URL + '/devicetypes', headers=headers, timeout=gTimeout)
            if response.status_code == 200:
                device_types = response.json()
                if object['type'] in device_types:
                    foi_to_send['device'] = object['type']
            else:
                print(str(response.status_code) + "FAIL RETRIEVING DEVICE TYPES")
        if 'geom' in object:
            foi_to_send['featureOfInterest']['geom'] = object['geom']
        if 'geom' in object:
            foi_to_send['featureOfInterest']['geom'] = object['geom']
    if __update_foi_file() or always_update:
        requests.post(HTTP_ + gServer + FOI_URL, json.dumps(foi_to_send), headers=headers,
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
    if gBatchEnabled:
        if not thread.is_alive():
            thread.start()
    else:
        if thread.is_alive():
            thread.join()
    return gBatchEnabled


def sendObservations(values):
    response = None
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    try:
        response = requests.put(HTTP_ + gServer + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}),
                                headers=headers, timeout=gTimeout)
    except Exception as e:
        print(e)
    if response is not None:
        if response.status_code >= 400:
            print(response.text)
        return response.status_code
    else:
        print("NO RESPONSE FROM SERVICE")
        return 502


def sendRecord(serie_id, observations):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    if isinstance(observations, str):
        response = requests.put(HTTP_ + gServer + PUBLISH_RECORD_URL + "/" + str(serie_id), observations,
                                headers=headers)
    else:
        response = requests.put(HTTP_ + gServer + PUBLISH_RECORD_URL + "/" + str(serie_id),
                                data=json.dumps(observations), headers=headers)
    return response.status_code, response.content


def sendObservationsCSV(values):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    response = requests.post(HTTP_ + gServer + PUBLISH_PLAIN_CSV_URL, data=values, headers=headers,
                             timeout=gTimeout)
    if response.status_code >= 400:
        print(response.text)
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
    r = requests.post(HTTP_ + gServer + GET_OBSERVATIONS_URL, data=json.dumps(message), headers=headers,
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
        device_type=None,
        foi_name=None
):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    message = getObservation(value, property, uom, ts, geom, procedure, foi, device_type, foi_name)
    json_payload = json.dumps(message)
    response = requests.put(HTTP_ + gServer + PUBLISH_SINGLE_URL, json_payload, headers=headers, timeout=gTimeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


def getObservation(
        value,
        property,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
        device_type=None,
        foi_name=None
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
    if device_type is not None:
        message['deviceType'] = device_type
    if foi_name is not None:
        message['foiName'] = foi_name
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
    response = requests.get(HTTP_ + gServer + SERIES_URL + foi + '/' + procedure + '/' + observable_property,
                            headers=headers, timeout=gTimeout)
    if response.status_code != 200:
        print("Error retrieving series: " + foi + "-" + procedure + "-" + observable_property)
        return None
    try:
        message = json.loads(response.content.decode("utf-8"))
        return message
    except:
        return None


def save_text_metadata(key, value, foi=None):
    if foi is None or foi == '':
        foi = gFoi
    message = {'key': key.upper(), 'value': value, 'type': 'TEXT'}
    json_payload = json.dumps(message)
    response = requests.post(HTTP_ + gServer + DEVICE_METADATA_URL + '/identifier/' + foi, json_payload,
                             headers=headers, timeout=gTimeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


def save_date_metadata(key, value, foi=None):
    if foi is None or foi == '':
        foi = gFoi
    message = {'key': key.upper(), 'value': value, 'type': 'DATE'}
    json_payload = json.dumps(message)
    response = requests.post(HTTP_ + gServer + DEVICE_METADATA_URL + '/identifier/' + foi, json_payload,
                             headers=headers, timeout=gTimeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


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

        response = requests.get(HTTP_ + gServer + (SOCKET_URL if url is None else url), headers=headers)
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

        response = requests.get(HTTP_ + gServer + SOCKET_URL, headers=headers)
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
            if clientTCPSocket is not None:
                clientTCPSocket.settimeout(15.0)
        return clientTCPSocket
    else:
        global clientUDPSocket
        if clientTCPSocket is None:
            clientUDPSocket = __get_udp_socket()
        return clientUDPSocket


def __get_payload(series_id, value, timestamp, protocol):
    if protocol is None or protocol.upper() == "TCP":
        return json.dumps(
            {
                'seriesId': series_id,
                'obs': [{
                    'seriesId': series_id,
                    'timestamp': timestamp,
                    'value': value
                }]
            }) + "\n"
    else:
        return json.dumps({
            'X-AUTH-TOKEN': headers['x-auth-token'],
            'data': {
                'seriesId': series_id,
                'obs': [{
                    'seriesId': series_id,
                    'timestamp': timestamp,
                    'value': value
                }]
            }
        })


def __reset_socket(protocol):
    if protocol is None or protocol.upper() == "TCP":
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
    global gBatchEnabled
    if gBatchEnabled:
        __save_batch_socket(series_id, value, timestamp)
    else:
        __send_socket(series_id, value, timestamp, protocol)


def __save_batch_socket(series_id, value, timestamp):
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
            __print__(e_message)
            return e_message
    else:
        gRealTimeAcumulator[str(series_id)] = [{
            'seriesId': series_id,
            'timestamp': timestamp,
            'value': value
        }]
    lock.release()


def __send_socket(series_id, value, timestamp, protocol=None):
    global gLastRealTimeTimestamp
    if gLastRealTimeTimestamp is None or int(time.time() * 1000) - gLastRealTimeTimestamp >= gRealTimeTimeout:
        clientSocket = __get_socket(protocol)

        if clientSocket is not None:
            json_payload = __get_payload(series_id, value, timestamp, protocol)
            try:
                clientSocket.sendall(json_payload.encode("utf-8"))
                try:
                    clientSocket.recv(1024)
                except socket.timeout:
                    print("Buffer was already empty")
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
    while True:
        global gBatchEnabled
        if gBatchEnabled:
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
                        try:
                            clientSocket.recv(1024)
                        except socket.timeout:
                            print("Buffer was already empty")
                except (socket.error, socket.timeout) as msg:
                    __print__("SOCKET ERROR:" + str(msg))
                    __reset_socket(protocol)
            else:
                lock.release()
                __print__("ERROR CONNECTING TO SOCKET")
        time.sleep(5)


def __register_action(
        name,
        parameter_type=None,
        foi=None,
        procedure=None,
        observable_property=None,
        unit=None,
        alias=None,
        action_options=None
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
        if action_options is not None and parameter_type.name == ActionDataTypes.SELECTOR.name:
            payload["actionOptions"] = action_options
        response = requests.post(HTTP_ + gServer + ACTIONS_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 201:
            return True
        else:
            print(response.status_code)
    except Exception as e:
        print(e)
    return None


def registerActionForSeries(name, observableProperty, unit, callback, foi=None, procedure=None, parameterType=None,
                            alias=None, action_options=None):
    result = __register_action(name, parameterType, foi, procedure, observableProperty, unit, alias=alias,
                               action_options=action_options)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback': callback, 'parameterType': parameterType}
        else:
            return False
    return result is not None


def registerAction(name, callback, foi=None, parameterType=None, alias=None, action_options=None):
    result = __register_action(name, parameterType, foi, alias=alias, action_options=action_options)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback': callback, 'parameterType': parameterType}
        else:
            return False
    return result is not None


def __action_socket_client(actionThreadStop, callbacks, foi):
    global gActionSocket
    current_time = time.time()
    gActionSocket = None
    while not actionThreadStop.is_set():
        action_time = time.time()
        try:
            if gActionSocket is None:
                gActionSocket = __get_tcp_socket(ACTIONS_URL)
            gActionSocket.settimeout(60.0)
            data = gActionSocket.recv(1024)
            decodedData = data.decode("utf-8")
            if decodedData != '':
                __parse_decoded_data(decodedData, gActionSocket, foi)
            try:
                if action_time - current_time > 5:
                    gActionSocket.sendall("Ping\n".encode("utf-8"))
                    current_time = time.time()
            except:
                print("The server closed the connection!")
                gActionSocket.close()
                gActionSocket = None
        except socket.timeout:
            print("timeout")
            gActionSocket.close()
            gActionSocket = None
            time.sleep(30)
            # __action_socket_client(actionThreadStop, callbacks, foi)
        except Exception as e:
            print(str(e))
            if str(e) != "'@PING@'":
                print("INTERNAL_FAILURE")
                gActionSocket.close()
                gActionSocket = None
                time.sleep(30)
                # __action_socket_client(actionThreadStop, callbacks, foi)
    gActionSocket.close()


def __parse_decoded_data(decoded_data, action_socket, foi):
    if decoded_data == "DEVICE":
        action_socket.sendall((foi + "\n").encode("utf-8"))
    else:
        if '@PING@' not in decoded_data:
            response = json.loads(decoded_data)
            param = None
            ts = response["timestamp"]
            command = response["name"]
            action_log = response["actionLog"]
            if 'action' in response:
                param = response["action"]
            # if callbacks[command] is not None:
            if command in callbacks:
                try:
                    sig = signature(callbacks[command]['callback'])
                    if len(sig.parameters) == 0:
                        result = callbacks[command]['callback']()
                    elif len(sig.parameters) == 1:
                        result = callbacks[command]['callback'](
                            __cast_parameter(param, callbacks[command]['parameterType']))
                    elif len(sig.parameters) == 2:
                        result = callbacks[command]['callback'](
                            __cast_parameter(param, callbacks[command]['parameterType']), ts)
                    else:
                        result = callbacks[command]['callback'](
                            __cast_parameter(param, callbacks[command]['parameterType']), ts, action_log)
                except Exception as e:
                    print(e)
                    print("ERROR DOING ACTION")
                    result = e
                try:
                    if result == 0 or isinstance(result, str):
                        action_socket.sendall((str(result).replace('\n', '') + '\n').encode("utf-8"))
                    else:
                        action_socket.sendall("\n".encode("utf-8"))
                except Exception as e:
                    print(e)
                    print("ERROR SENDING RESPONSE")


def __cast_parameter(param, parameter_type):
    text_actions = [ActionDataTypes.TEXT, ActionDataTypes.FILE, ActionDataTypes.SELECTOR, ActionDataTypes.LIVE,
                    ActionDataTypes.JSON, ActionDataTypes.DATE]
    try:
        if parameter_type is None:
            return None
        elif parameter_type in text_actions:
            return param
        elif parameter_type == ActionDataTypes.ARRAY:
            return param.split(";")
        elif parameter_type == ActionDataTypes.BOOLEAN:
            return param.lower() == 'true'
        elif parameter_type == ActionDataTypes.NUMBER:
            return ast.literal_eval(param)  # Number
    except:
        return None


def sendProgressAction(message):
    try:
        global gActionSocket
        if gActionSocket is None:
            raise Exception("Action Socket is not available")
        if message == 0 or isinstance(message, str):
            gActionSocket.sendall((str(message).replace('\n', '') + '\n').encode("utf-8"))
        else:
            gActionSocket.sendall("\n".encode("utf-8"))
    except Exception as e:
        print(e)
        print("ERROR SENDING PROGRESS ACTION")


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


def api_get_request(url):
    response = requests.get(HTTP_ + gServer + url, headers=headers, timeout=gTimeout)
    return response.status_code, json.loads(response.text)


def send_alert(self, subject, text):
    response = requests.post(HTTP_ + gServer + DEVICE_ALERT_URL, data=json.dumps({
        "subject": subject,
        "text": text
    }), headers=headers)
    return response.status_code, json.loads(response.text)


def __print__(text):
    print(text)
    sys.stdout.flush()


if not os.path.exists(".foiCache"):
    f = open(".foiCache", "a")
    f.close()

thread = Thread(target=__send_socket_batch)
lock = Lock()
