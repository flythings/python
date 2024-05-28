#!/usr/bin/python
# -*- coding: utf-8 -*-
import ast
import base64
import copy
import json
import os
import socket
import sys
import time
from datetime import timedelta, datetime
from enum import Enum
from inspect import signature
from threading import Thread, Event, Lock
from urllib.parse import urlparse

import requests

HTTP_ = 'http://'
HTTPS_ = 'https://'

PUBLISH_MULTIPLE_URL = '/observation/multiple'
PUBLISH_PREDICTION_MULTIPLE_URL = '/prediction/multiple'
GET_OBSERVATIONS_URL = '/observation'
GET_PREDICTIONS_URL = '/prediction'
PUBLISH_SINGLE_URL = '/observation/single'
PUBLISH_PREDICTION_SINGLE_URL = '/prediction/single'
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
PUBLISH_INFRASTRUCTURE = '/featuretag'
PUBLISH_INFRASTRUCTURE_METADATA = '/featuretag/withmetadata'
PUBLISH_INFRASTRUCTURE_SIMPLE = '/featuretag/simple'
FILE = 'Configuration.properties'

headers = {'x-auth-token': '', 'Content-Type': 'application/json'}

client_tcp_socket = None
client_udp_socket = None
client_action_thread = None
callbacks = {}
action_thread_stop = False

g_foi = ''
g_procedure = ''
g_server = ''
g_user = ''
g_password = ''
g_hash = ''
g_workspace = ''
g_timeout = 1000
g_real_time_acumulator = {}
g_batch_enabled = False
g_batch_timeout = 50
g_real_time_timeout = 1400
g_last_real_time_timestamp = None

g_action_socket = None


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


class SamplingFeatureType(Enum):
    POINT = {
        'id': 1,
        'type': 'http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingPoint'
    }
    LINE = {
        'id': 2,
        'type': 'http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingSurface'
    }
    POLYGON = {
        'id': 3,
        'type': 'http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_Specimen'
    }
    NO_POSITION = {
        'id': 4,
        'type': 'http://www.opengis.net/def/samplingFeatureType/OGC-OM/2.0/SF_SamplingCurve'
    }


def login(user, password, login_type):
    try:
        if login_type == 'DEVICE':
            authbody = requests.get(g_server + LOGIN_DEVICE_URL, auth=(user, password), timeout=g_timeout)
        elif login_type == 'USER':
            authbody = requests.get(g_server + LOGIN_USER_URL, auth=(user, password), timeout=g_timeout)
        else:
            login_type = 'USER'
            authbody = requests.get(g_server + LOGIN_USER_URL, auth=(user, password), timeout=g_timeout)
        if authbody.status_code == 200:
            global headers
            body = json.loads(authbody.text)
            headers['x-auth-token'] = str(body['token'])
            if login_type == 'USER' and 'workspace' in body:
                headers['Workspace'] = str(body['workspace'])
            else:
                headers['Workspace'] = str(g_workspace)
            return str(body['token'])
        else:
            print('ERROR AUTHENTICATED, CHECK THE USER OR PASSWORD')
            return None
    except requests.exceptions.InvalidURL:
        print('INVALID SERVER')
        raise


def logout():
    global headers
    headers.pop('x-auth-token', None)
    headers['x-auth-token'] = ''
    headers.pop('Workspace', None)
    headers.pop('Authorization', None)


def load_data_by_file(file=None):
    if file is None:
        file = FILE
    global g_server
    try:
        for line in open(file):
            text = line.strip().replace('\n', '')
            list_param = text.split(':')
            __update_file_params(list_param)
        if g_user != '' and g_password != '':
            login(g_user, g_password, g_login_type)
        global g_server
        if g_server == '':
            g_server = 'api.flythings.io'
        print('Succesfully loaded data from file ' + file)
    except Exception:
        print('CONFIGURATION FILE, ' + file + ' DONT EXIST, YOU MUST INSERT THE PARAMETERS MANUALLY')


def __update_file_params(list_param):
    if len(list_param) > 1:
        global headers
        if list_param[0].lower() == 'token':
            list_param[1] = list_param[1].strip()
            global gToken
            gToken = list_param[1]
            headers['x-auth-token'] = list_param[1]
        elif list_param[0].lower() == 'server':
            global g_server
            list_param[1] = list_param[1].strip()
            g_server = list_param[1]
        elif list_param[0].lower() == 'user':
            list_param[1] = list_param[1].strip()
            global g_user
            g_user = list_param[1]
        elif list_param[0].lower() == 'password':
            list_param[1] = list_param[1].strip()
            global g_password
            g_password = list_param[1]
        elif list_param[0].lower() == 'login_type':
            list_param[1] = list_param[1].strip()
            global g_login_type
            g_login_type = list_param[1]
        elif list_param[0].lower() == 'hash':
            list_param[1] = list_param[1].strip()
            global g_hash
            g_hash = list_param[1]
        elif list_param[0].lower() == 'device':
            list_param[1] = list_param[1].strip()
            global g_foi
            g_foi = list_param[1]
        elif list_param[0].lower() == 'sensor':
            list_param[1] = list_param[1].strip()
            global g_procedure
            g_procedure = list_param[1]
        elif list_param[0].lower() == 'timeout':
            list_param[1] = list_param[1].strip()
            global g_timeout
            g_timeout = list_param[1]
        elif list_param[0].lower() == 'authorization':
            headers['Authorization'] = "Bearer " + list_param[1]
            headers['x-auth-token'] = '-'


def set_server(server):
    global g_server
    if server is not None:
        server = server.strip()
        if server.endswith('/'):
            server = server[:-1]
        if not server.startswith(HTTP_) and not server.startswith(HTTPS_):
            server = HTTP_ + server
        g_server = server
    return g_server


def get_server():
    global g_server
    return g_server


def __update_foi_file():
    file = open(".foiCache", "r")
    for line in file:
        line_items = line.split('\t')
        if line_items[0] == g_server and line_items[1] == g_foi:
            return False
    file.close()
    file = open('.foiCache', 'a')
    file.write(g_server + '\t' + g_foi + '\t' + '\n')
    file.close()
    return True


def set_device(device, object=None, always_update=False):
    global g_foi
    g_foi = device
    foi_to_send = {'featureOfInterest': {"name": device}}
    if object is not None:
        if 'type' in object:
            response = requests.get(g_server + FOI_URL + '/devicetypes', headers=headers, timeout=g_timeout)
            if response.status_code == 200:
                device_types = response.json()
                if object['type'] in device_types:
                    foi_to_send['device'] = object['type']
            else:
                print(str(response.status_code) + "FAIL RETRIEVING DEVICE TYPES")
        if 'geom' in object:
            foi_to_send['featureOfInterest']['geom'] = object['geom']
    if __update_foi_file() or always_update:
        requests.post(g_server + FOI_URL, json.dumps(foi_to_send), headers=headers,
                      timeout=g_timeout)
    return g_foi


def set_custom_header(header, header_value):
    global headers
    headers[header] = header_value
    return headers[header]


def get_headers():
    global headers
    return headers


def set_sensor(sensor):
    global g_procedure
    g_procedure = sensor
    return g_procedure


def set_token(token):
    global headers
    headers['x-auth-token'] = token
    return headers['x-auth-token']


def set_authorization_token(token):
    global headers
    headers['Authorization'] = "Bearer " + token
    headers['x-auth-token'] = '-'
    return headers['Authorization']


def set_workspace(workspace):
    global g_workspace
    g_workspace = workspace
    return g_workspace


def set_timeout(timeout):
    global g_timeout
    g_timeout = timeout
    return g_timeout


def set_batch_enabled(batch_enabled):
    global g_batch_enabled
    global thread
    g_batch_enabled = batch_enabled
    if g_batch_enabled:
        if not thread.is_alive():
            thread.start()
    else:
        if thread.is_alive():
            thread.join()
    return g_batch_enabled


def send_observations(values):
    response = None
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return response
    if values is None:
        print('Values cannot be None')
        return response
    if len(values) > 1000:
        i = 0
        while i < len(values):
            aux_values = values[i:i + 1000]
            response = __send_observations(aux_values)
            if response >= 400:
                return response
            i += 1000
    else:
        response = __send_observations(values)
    return response


def __send_observations(values):
    response = None
    try:
        response = requests.put(g_server + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}),
                                headers=headers, timeout=g_timeout)
    except Exception as e:
        print(e)
    if response is not None:
        if response.status_code >= 400:
            print(response.text)
        return response.status_code
    else:
        print("NO RESPONSE FROM SERVICE")
        return 502


def send_predictions(values):
    response = None
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return response
    if values is None:
        print('Values cannot be None')
        return response
    if len(values) > 1000:
        i = 0
        while i < len(values):
            aux_values = values[i:i + 1000]
            response = __send_predictions(aux_values)
            if response >= 400:
                return response
            i += 1000
    else:
        response = __send_predictions(values)
    return response


def __send_predictions(values):
    response = None
    try:
        response = requests.put(g_server + PUBLISH_PREDICTION_MULTIPLE_URL, data=json.dumps({'predictions': values}),
                                headers=headers, timeout=g_timeout)
    except Exception as e:
        print(e)
    if response is not None:
        if response.status_code >= 400:
            print(response.text)
        return response.status_code
    else:
        print("NO RESPONSE FROM SERVICE")
        return 502


def send_record(serie_id, observations):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    if isinstance(observations, str):
        response = requests.put(g_server + PUBLISH_RECORD_URL + "/" + str(serie_id), observations,
                                headers=headers)
    else:
        response = requests.put(g_server + PUBLISH_RECORD_URL + "/" + str(serie_id),
                                data=json.dumps(observations), headers=headers)
    return response.status_code, response.content


def send_observations_csv(values):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    response = requests.post(g_server + PUBLISH_PLAIN_CSV_URL, data=values, headers=headers,
                             timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code, response.content


def search(
        series,
        start_date=None,
        end_date=None,
        aggrupation=None,
        aggrupation_type=None,
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
    if aggrupation_type is not None:
        message['temporalScaleType'] = aggrupation_type
    r = requests.post(g_server + GET_OBSERVATIONS_URL, data=json.dumps(message), headers=headers,
                      timeout=g_timeout)
    if r.status_code == 200:
        list = r.json()[0]['data']
        return_list = []
        for elem in list:
            return_list.append({'value': elem[1], 'time': elem[0]})
        return return_list
    else:
        print(r.text)


def search_prediction(
        series,
        start_date=None,
        end_date=None,
        aggrupation=None,
        aggrupation_type=None,
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
    if aggrupation_type is not None:
        message['temporalScaleType'] = aggrupation_type
    r = requests.post(g_server + GET_PREDICTIONS_URL, data=json.dumps(message), headers=headers,
                      timeout=g_timeout)
    if r.status_code == 200:
        list = r.json()[0]['data']
        return_list = []
        for elem in list:
            return_list.append({'value': elem[1], 'time': elem[0]})
        return return_list
    else:
        print(r.text)


def send_observation(
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
    message = get_observation(value, property, uom, ts, geom, procedure, foi, device_type, foi_name)
    json_payload = json.dumps(message)
    response = requests.put(g_server + PUBLISH_SINGLE_URL, json_payload, headers=headers, timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


def send_prediction(
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
    message = get_observation(value, property, uom, ts, geom, procedure, foi, device_type, foi_name)
    json_payload = json.dumps(message)
    response = requests.put(g_server + PUBLISH_PREDICTION_SINGLE_URL, json_payload, headers=headers,
                            timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


def get_image_observation(
        file,
        property,
        format=None,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
        device_type=None,
        foi_name=None
):
    if isinstance(file, str):
        with open(file, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
            f = b64_string.decode('utf-8')
        if file.rsplit(".") is not None and len(file.rsplit(".")) > 1:
            format = file.rsplit(".")[1]
    else:
        f = base64.b64encode(file.read()).decode('utf-8')
    if format is None:
        print('Format cannot be None')
        return None
    message = {'observableProperty': property, "file": {"file": f, "format": format}}
    if uom is not None:
        message['uom'] = uom
    if ts is not None:
        message['time'] = ts
    if geom is not None:
        message['geom'] = geom
    if procedure is not None and procedure != '':
        message['procedure'] = procedure
    else:
        message['procedure'] = g_procedure
    if foi is not None and foi != '':
        message['foi'] = foi
    else:
        message['foi'] = g_foi
    if device_type is not None:
        message['deviceType'] = device_type
    if foi_name is not None:
        message['foiName'] = foi_name
    return message


def get_image_bytes_observation(
        bytes,
        property,
        format,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
        device_type=None,
        foi_name=None
):
    f = base64.b64encode(bytes).decode('utf-8')
    message = {'observableProperty': property, "file": {"file": f, "format": format}}
    if uom is not None:
        message['uom'] = uom
    if ts is not None:
        message['time'] = ts
    if geom is not None:
        message['geom'] = geom
    if procedure is not None and procedure != '':
        message['procedure'] = procedure
    else:
        message['procedure'] = g_procedure
    if foi is not None and foi != '':
        message['foi'] = foi
    else:
        message['foi'] = g_foi
    if device_type is not None:
        message['deviceType'] = device_type
    if foi_name is not None:
        message['foiName'] = foi_name
    return message


def get_image_base64_observation(
        base_64,
        property,
        format,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
        device_type=None,
        foi_name=None
):
    f = base_64.decode('utf-8')
    message = {'observableProperty': property, "file": {"file": f, "format": format}}
    if uom is not None:
        message['uom'] = uom
    if ts is not None:
        message['time'] = ts
    if geom is not None:
        message['geom'] = geom
    if procedure is not None and procedure != '':
        message['procedure'] = procedure
    else:
        message['procedure'] = g_procedure
    if foi is not None and foi != '':
        message['foi'] = foi
    else:
        message['foi'] = g_foi
    if device_type is not None:
        message['deviceType'] = device_type
    if foi_name is not None:
        message['foiName'] = foi_name
    return message


def get_observation(
        value,
        property,
        uom=None,
        ts=None,
        geom=None,
        procedure=None,
        foi=None,
        device_type=None,
        foi_name=None,
        force_type=None
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
        message['procedure'] = g_procedure
    if foi is not None and foi != '':
        message['foi'] = foi
    else:
        message['foi'] = g_foi
    if device_type is not None:
        message['deviceType'] = device_type
    if foi_name is not None:
        message['foiName'] = foi_name
    if force_type is not None:
        message['forceType'] = force_type
    return message


def get_observation_csv(
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
            message += g_foi + ";"
        if procedure is not None:
            message += procedure + ";"
        else:
            message += g_procedure + ";"
        if property is not None:
            message += property + ";"
        else:
            return None
    if ts is not None:
        message += str(ts)
    else:
        message += str(int(time.time() * 1000))
    message += ";" + value
    if uom is not None:
        message += ";" + uom
    return message


def find_series(foi=None, procedure=None, observable_property=None):
    if foi is None or foi == '':
        foi = g_foi
    if procedure is None or procedure == '':
        procedure = g_procedure
    if observable_property is None or observable_property == '':
        return "INSERT A OBSERVABLE PROPERTY"
    response = requests.get(g_server + SERIES_URL + foi + '/' + procedure + '/' + observable_property,
                            headers=headers, timeout=g_timeout)
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
        foi = g_foi
    message = {'key': key.upper(), 'value': value, 'type': 'TEXT'}
    json_payload = json.dumps(message)
    response = requests.put(g_server + DEVICE_METADATA_URL + '/identifier/' + foi, json_payload,
                            headers=headers, timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


def save_date_metadata(key, value, foi=None):
    if foi is None or foi == '':
        foi = g_foi
    message = {'key': key.upper(), 'value': value, 'type': 'DATE'}
    json_payload = json.dumps(message)
    response = requests.put(g_server + DEVICE_METADATA_URL + '/identifier/' + foi, json_payload,
                            headers=headers, timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
    return response.status_code


def get_text_metadata(key, value, tag_id=None):
    metadata = {'key': key.upper(), 'value': value, 'tagId': tag_id, 'type': 'TEXT'}
    return metadata


def get_infrastructure(
        name,
        type,
        geom=None,
        geom_type=None,
        fois=None,
        alias=None
):
    infrastructure = {'name': name, 'type': type}
    if alias is not None:
        infrastructure['alias'] = alias
    if geom is not None:
        infrastructure['geom'] = geom
    if geom_type is not None and geom_type.value is not None:
        infrastructure['geomType'] = geom_type.value
    else:
        infrastructure['geomType'] = SamplingFeatureType.NO_POSITION.value
    if fois is not None and fois:
        infrastructure['featureOfInterestList'] = fois
    return infrastructure


def get_infrastructure_withmetadata(
        name,
        type,
        geom=None,
        geom_type=None,
        fois=None,
        text_metadata_list=None,
        alias=None
):
    infrastructure = {'name': name, 'type': type}
    if alias is not None:
        infrastructure['alias'] = alias
    if geom is not None:
        infrastructure['geom'] = geom
    if geom_type is not None and geom_type.value is not None:
        infrastructure['geomType'] = geom_type.value
    else:
        infrastructure['geomType'] = SamplingFeatureType.NO_POSITION.value
    if fois is not None and fois:
        infrastructure['featureOfInterestList'] = fois
    if text_metadata_list is not None and text_metadata_list != '':
        infrastructure['textMetadata'] = text_metadata_list
    return infrastructure


def save_infrastructure(infrastructure, id=None):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None, None
    if id is not None:
        infrastructure.id = id
    json_payload = json.dumps(infrastructure)
    response = requests.post(g_server + PUBLISH_INFRASTRUCTURE_METADATA,
                             json_payload, headers=headers, timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
        return response.status_code, None
    return response.status_code, json.loads(response.text)


def save_infrastructure_with_metadata(infrastructure, id=None):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None, None
    if id is not None:
        infrastructure.id = id
    json_payload = json.dumps(infrastructure)
    response = requests.post(g_server + PUBLISH_INFRASTRUCTURE_METADATA,
                             json_payload, headers=headers, timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
        return response.status_code, None
    return response.status_code, json.loads(response.text)


def save_infrastructure_without_override_fois(infrastructure, id=None):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None, None
    if id is not None:
        infrastructure.id = id
    json_payload = json.dumps(infrastructure)
    response = requests.post(g_server + PUBLISH_INFRASTRUCTURE_SIMPLE,
                             json_payload, headers=headers, timeout=g_timeout)
    if response.status_code >= 400:
        print(response.text)
        return response.status_code, None
    return response.status_code, json.loads(response.text)


def link_device_to_infrastructure(infrastructure_tree, foi_identifier):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    if foi_identifier is None:
        print('foi_identifier is None')
        return None
    json_payload = json.dumps(infrastructure_tree)
    response = requests.put(
        g_server + PUBLISH_INFRASTRUCTURE + "/link/featureofinterest/" + foi_identifier,
        json_payload, headers=headers, timeout=g_timeout)
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
        response = requests.get(g_server + (SOCKET_URL if url is None else url), headers=headers)
        if response.status_code == 200:
            port = int(response.text)
            url = urlparse(g_server)
            s.connect((url.hostname, port))

            data = s.recv(1024)

            if decode(data) == 'X-AUTH-TOKEN':
                if 'Authorization' in headers and headers['Authorization'] is not None \
                        and headers['x-auth-token'] == '-':
                    s.sendall((headers['Authorization'] + "\n").encode("utf-8"))
                else:
                    s.sendall((headers['x-auth-token'] + "\n").encode("utf-8"))
                is_logged = s.recv(4)
                if decode(is_logged) == 'True':
                    return s
                else:
                    print("INVALID_TOKEN")
                    s.close()
            else:
                print("SOCKET UNAVAILABLE!")
                s.close()
    except:
        print("Connection refused")
    return None


def __get_udp_socket():
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if ":" not in g_server:
            if "/" not in g_server:
                server = g_server
            else:
                server = g_server.split("/")[0]
        else:
            server = g_server.split(":")[0]

        response = requests.get(g_server + SOCKET_URL, headers=headers)
        if response.status_code == 200:
            port = int(response.text)

            s.connect((server, port))
            return s
    except:
        print("Connection refused")
    return None


def __get_socket(protocol):
    if protocol is None or protocol.upper() == "TCP":
        global client_tcp_socket
        if client_tcp_socket is None:
            client_tcp_socket = __get_tcp_socket()
            if client_tcp_socket is not None:
                client_tcp_socket.settimeout(15.0)
        return client_tcp_socket
    else:
        global client_udp_socket
        if client_tcp_socket is None:
            client_udp_socket = __get_udp_socket()
        return client_udp_socket


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
        global client_tcp_socket
        if client_tcp_socket is not None:
            client_tcp_socket.close()
            client_tcp_socket = None
    else:
        global client_udp_socket
        if client_udp_socket is not None:
            client_udp_socket.close()
            client_udp_socket = None


def send_socket(series_id, value, timestamp, protocol=None):
    global g_batch_enabled
    if g_batch_enabled:
        __save_batch_socket(series_id, value, timestamp)
    else:
        __send_socket(series_id, value, timestamp, protocol)


def __save_batch_socket(series_id, value, timestamp):
    lock.acquire()
    global g_real_time_acumulator
    global g_batch_timeout
    if str(series_id) in g_real_time_acumulator:
        if int(time.time() * 1000) - \
                g_real_time_acumulator[str(series_id)][len(g_real_time_acumulator[str(series_id)]) - 1][
                    'timestamp'] >= g_batch_timeout:
            g_real_time_acumulator[str(series_id)].append({
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
        g_real_time_acumulator[str(series_id)] = [{
            'seriesId': series_id,
            'timestamp': timestamp,
            'value': value
        }]
    lock.release()


def __send_socket(series_id, value, timestamp, protocol=None):
    global g_last_real_time_timestamp
    if g_last_real_time_timestamp is None or int(
            time.time() * 1000) - g_last_real_time_timestamp >= g_real_time_timeout:
        client_socket = __get_socket(protocol)

        if client_socket is not None:
            json_payload = __get_payload(series_id, value, timestamp, protocol)
            try:
                client_socket.sendall(json_payload.encode("utf-8"))
                try:
                    client_socket.recv(1024)
                except socket.timeout:
                    print("Buffer was already empty")
            except socket.error as msg:
                __reset_socket(protocol)
                print(msg)
        else:
            print("ERROR CONNECTING TO SOCKET")
        print('CORRECT SENDED')
        g_last_real_time_timestamp = int(time.time() * 1000)
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
        global g_batch_enabled
        if g_batch_enabled:
            client_socket = __get_socket(protocol)
            lock.acquire()
            global g_real_time_acumulator
            acumulator = copy.deepcopy(g_real_time_acumulator)
            if client_socket is not None:
                g_real_time_acumulator = {}
                lock.release()
                try:
                    values = acumulator.values()
                    for value in values:
                        json_payload = __acumulator_series_to_json(value)
                        client_socket.sendall(json_payload.encode("utf-8"))
                        try:
                            client_socket.recv(1024)
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
        action_options=None,
        json_template=None
):
    if headers['x-auth-token'] == '':
        print('NoAuthenticationError')
        return None
    elif foi is None and g_foi is None:
        print('NoDeviceError')
        return None
    elif observable_property is not None and (g_procedure is None and procedure is None):
        print('NoProcedureError')
        return None
    try:
        payload = {
            "name": name,
            "featureOfInterest": g_foi if foi is None else foi,
            "parameterType": ActionDataTypes(parameter_type).name if parameter_type is not None else None
        }
        if observable_property is not None:
            payload["procedure"] = g_procedure if procedure is None else procedure
            payload["observableProperty"] = observable_property
        if unit is not None:
            payload["unit"] = unit
        if alias is not None:
            payload["alias"] = alias
        if action_options is not None and parameter_type.name == ActionDataTypes.SELECTOR.name:
            payload["actionOptions"] = action_options
        if json_template is not None:
            payload["jsonTemplate"] = json_template
        response = requests.post(g_server + ACTIONS_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 201:
            return True
        else:
            print(response.status_code)
    except Exception as e:
        print(e)
    return None


def register_action_for_series(name, observable_property, unit, callback, foi=None, procedure=None, parameter_type=None,
                               alias=None, action_options=None, json_template=None):
    result = __register_action(name, parameter_type, foi, procedure, observable_property, unit, alias=alias,
                               action_options=action_options, json_template=json_template)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback': callback, 'parameterType': parameter_type}
        else:
            return False
    return result is not None


def register_action(name, callback, foi=None, parameter_type=None, alias=None, action_options=None,
                    json_template=None):
    result = __register_action(name, parameter_type, foi, alias=alias, action_options=action_options,
                               json_template=json_template)
    if result:
        global callbacks
        if name not in callbacks:
            callbacks[name] = {'callback': callback, 'parameterType': parameter_type}
        else:
            return False
    return result is not None


def __action_socket_client(action_thread_stop, callbacks, foi):
    global g_action_socket
    current_time = time.time()
    g_action_socket = None
    while not action_thread_stop.is_set():
        action_time = time.time()
        try:
            if g_action_socket is None:
                g_action_socket = __get_tcp_socket(ACTIONS_URL)
            if g_action_socket is not None:
                g_action_socket.settimeout(60.0)
                data = g_action_socket.recv(1024)
                decoded_data = data.decode("utf-8")
                if decoded_data != '':
                    __parse_decoded_data(decoded_data, g_action_socket, foi)
                try:
                    if action_time - current_time > 5:
                        g_action_socket.sendall("Ping\n".encode("utf-8"))
                        current_time = time.time()
                except:
                    print("The server closed the connection!")
                    g_action_socket.close()
                    g_action_socket = None
            else:
                print("Could not open Action socket, waiting 30 secs to retry")
                time.sleep(30)
        except socket.timeout:
            print("timeout")
            g_action_socket.close()
            g_action_socket = None
            time.sleep(30)
            # __action_socket_client(actionThreadStop, callbacks, foi)
        except Exception as e:
            print(str(e))
            if str(e) != "'@PING@'":
                print("INTERNAL_FAILURE")
                if g_action_socket is not None:
                    g_action_socket.close()
                    g_action_socket = None
                time.sleep(30)
                # __action_socket_client(actionThreadStop, callbacks, foi)
    g_action_socket.close()


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


def send_progress_action(message):
    try:
        global g_action_socket
        if g_action_socket is None:
            raise Exception("Action Socket is not available")
        if message == 0 or isinstance(message, str):
            g_action_socket.sendall((str(message).replace('\n', '') + '\n').encode("utf-8"))
        else:
            g_action_socket.sendall("\n".encode("utf-8"))
    except Exception as e:
        print(e)
        print("ERROR SENDING PROGRESS ACTION")


def start_action_listening(foi=None):
    if foi is not None and foi != '':
        f = foi
    else:
        f = g_foi
    if f is None or f == '':
        print("NoDeviceException")
        return None
    if not callbacks:
        print("NoRegisteredActionExcetion")
        return None
    global action_thread_stop, client_action_thread
    action_thread_stop = Event()
    client_action_thread = Thread(target=__action_socket_client, args=(action_thread_stop, callbacks, f))
    client_action_thread.start()


def stop_action_listening():
    global action_thread_stop, client_action_thread
    if action_thread_stop:
        action_thread_stop.set()
    client_action_thread = None


def api_get_request(url):
    response = requests.get(g_server + url, headers=headers, timeout=g_timeout)
    if response is not None:
        if response.status_code >= 400:
            response.status_code, response.text
    else:
        print("NO RESPONSE FROM SERVICE")
        return 502
    return response.status_code, json.loads(response.text)


def send_alert(subject, text):
    response = requests.put(g_server + DEVICE_ALERT_URL, data=json.dumps({
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
