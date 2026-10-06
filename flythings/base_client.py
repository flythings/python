#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import socket
import sys
from urllib.parse import urlparse

import requests

from flythings import ServerConfig
from flythings.paths import FOI_URL, HTTP_, HTTPS_, LOGIN_USER_URL, LOGIN_DEVICE_URL, SOCKET_URL, FILE


class BaseClient:
    thread = None
    lock = None

    headers = {'x-auth-token': '', 'Content-Type': 'application/json'}

    real_time_acumulator = {}
    batch_enabled = False
    batch_timeout = 50
    real_time_timeout = 1400
    last_real_time_timestamp = None
    action_socket = None

    client_tcp_socket = None
    client_udp_socket = None
    client_action_thread = None
    callbacks = {}
    action_thread_stop = False

    # class-level initialization (runs once when class is defined)
    if not os.path.exists(".foiCache"):
        f = open(".foiCache", "a")
        f.close()

    def __init__(self, config: ServerConfig):
        self.config = config
        # self.thread = Thread(target=self.__send_socket_batch)
        # self.lock = Lock()
        self.set_authorization_token(config.authorization)
        self.set_token(config.token)
        self.set_server(config.server)

    def login(self, user, password, login_type):
        try:
            if login_type == 'DEVICE':
                authbody = requests.get(self.config.server + LOGIN_DEVICE_URL, auth=(user, password),
                                        timeout=self.config.timeout)
            elif login_type == 'USER':
                authbody = requests.get(self.config.server + LOGIN_USER_URL, auth=(user, password),
                                        timeout=self.config.timeout)
            else:
                login_type = 'USER'
                authbody = requests.get(self.config.server + LOGIN_USER_URL, auth=(user, password),
                                        timeout=self.config.timeout)
            if authbody.status_code == 200:
                body = json.loads(authbody.text)
                self.headers['x-auth-token'] = str(body['token'])
                if login_type == 'USER' and 'workspace' in body:
                    self.headers['Workspace'] = str(body['workspace'])
                else:
                    self.headers['Workspace'] = str(self.config.workspace)
                return str(body['token'])
            else:
                print('ERROR AUTHENTICATED, CHECK THE USER OR PASSWORD')
                return None
        except requests.exceptions.InvalidURL:
            print('INVALID SERVER')
            raise

    def logout(self):
        self.headers.pop('x-auth-token', None)
        self.headers['x-auth-token'] = ''
        self.headers.pop('Workspace', None)
        self.headers.pop('Authorization', None)

    def load_data_by_file(self, file=None):
        if file is None:
            file = FILE
        try:
            for line in open(file):
                text = line.strip().replace('\n', '')
                list_param = text.split(':')
                self.__update_file_params(list_param)
            if self.config.user != '' and self.config.password != '':
                self.login(self.config.user, self.config.password, self.config.login_type)
            if self.config.server == '':
                self.config.server = 'api.flythings.io'
            print('Succesfully loaded data from file ' + file)
        except Exception:
            print('CONFIGURATION FILE, ' + file + ' DONT EXIST, YOU MUST INSERT THE PARAMETERS MANUALLY')

    def __update_file_params(self, list_param):
        if len(list_param) > 1:
            if list_param[0].lower() == 'token':
                list_param[1] = list_param[1].strip()
                self.config.token = list_param[1]
                self.headers['x-auth-token'] = list_param[1]
            elif list_param[0].lower() == 'server':
                list_param[1] = list_param[1].strip()
                self.config.server = list_param[1]
            elif list_param[0].lower() == 'user':
                list_param[1] = list_param[1].strip()
                self.config.user = list_param[1]
            elif list_param[0].lower() == 'password':
                list_param[1] = list_param[1].strip()
                self.config.password = list_param[1]
            elif list_param[0].lower() == 'login_type':
                list_param[1] = list_param[1].strip()
                self.config.login_type = list_param[1]
            elif list_param[0].lower() == 'hash':
                list_param[1] = list_param[1].strip()
                self.config.hash = list_param[1]
            elif list_param[0].lower() == 'device':
                list_param[1] = list_param[1].strip()
                self.config.foi = list_param[1]
            elif list_param[0].lower() == 'sensor':
                list_param[1] = list_param[1].strip()
                self.config.procedure = list_param[1]
            elif list_param[0].lower() == 'timeout':
                list_param[1] = list_param[1].strip()
                self.config.timeout = list_param[1]
            elif list_param[0].lower() == 'authorization':
                self.headers['Authorization'] = "Bearer " + list_param[1]
                self.headers['x-auth-token'] = '-'

    def set_server(self, server):
        if server is not None:
            server = server.strip()
            if server.endswith('/'):
                server = server[:-1]
            if not server.startswith(HTTP_) and not server.startswith(HTTPS_):
                server = HTTP_ + server
            self.config.server = server
        return self.config.server

    def get_server(self):
        return self.config.server

    def __update_foi_file(self):
        file = open(".foiCache", "r")
        for line in file:
            line_items = line.split('\t')
            if line_items[0] == self.config.server and line_items[1] == self.config.foi:
                return False
        file.close()
        file = open('.foiCache', 'a')
        file.write(self.config.server + '\t' + self.config.foi + '\t' + '\n')
        file.close()
        return True

    def set_device(self, device, object=None, always_update=False):
        self.config.foi = device
        foi_to_send = {'featureOfInterest': {"name": device}}
        if object is not None:
            if 'type' in object:
                response = requests.get(self.config.server + FOI_URL + '/devicetypes', headers=self.headers, timeout=self.config.timeout)
                if response.status_code == 200:
                    device_types = response.json()
                    if object['type'] in device_types:
                        foi_to_send['device'] = object['type']
                else:
                    print(str(response.status_code) + "FAIL RETRIEVING DEVICE TYPES")
            if 'geom' in object:
                foi_to_send['featureOfInterest']['geom'] = object['geom']
        if self.__update_foi_file() or always_update:
            requests.post(self.config.server + FOI_URL, json.dumps(foi_to_send), headers=self.headers,
                          timeout=self.config.timeout)
        return self.config.foi

    def set_custom_header(self, header, header_value):
        self.headers[header] = header_value
        return self.headers[header]

    def get_headers(self):
        return self.headers

    def set_sensor(self, sensor):
        self.config.procedure = sensor
        return self.config.procedure

    def set_token(self,token):
        self.headers['x-auth-token'] = token
        return self.headers['x-auth-token']

    def set_authorization_token(self, token):
        self.headers['Authorization'] = "Bearer " + token
        self.headers['x-auth-token'] = '-'
        return self.headers['Authorization']

    def set_workspace(self, workspace):
        self.config.workspace = workspace
        return self.config.workspace

    def set_timeout(self, timeout):
        self.config.timeout = timeout
        return self.config.timeout

    def set_batch_enabled(self, batch_enabled):
        self.batch_enabled = batch_enabled
        if self.batch_enabled :
            if not self.thread.is_alive():
                self.thread.start()
        else:
            if self.thread.is_alive():
                self.thread.join()
        return self.batch_enabled

    def __get_socket(self, protocol):
        if protocol is None or protocol.upper() == "TCP":
            if self.client_tcp_socket is None:
                self.client_tcp_socket = self.__get_tcp_socket()
                if self.client_tcp_socket is not None:
                    self.client_tcp_socket.settimeout(15.0)
            return self.client_tcp_socket
        else:
            if self.client_udp_socket is None:
                self.client_udp_socket = self.__get_udp_socket()
            return self.client_udp_socket

    def __acumulator_series_to_json(data):
        return json.dumps({'seriesId': data[0]['seriesId'],
                           'obs': sorted(data, key=lambda o: o['timestamp'])
                           }) + "\n"

    def __get_tcp_socket(self,url=None):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None

        decode = lambda d: d.decode('utf-8')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            response = requests.get(self.config.server + (SOCKET_URL if url is None else url), headers=self.headers)
            if response.status_code == 200:
                port = int(response.text)
                url = urlparse(self.config.server)
                s.connect((url.hostname, port))

                data = s.recv(1024)

                if decode(data) == 'X-AUTH-TOKEN':
                    if 'Authorization' in self.headers and self.headers['Authorization'] is not None \
                        and self.headers['x-auth-token'] == '-':
                        s.sendall((self.headers['Authorization'] + "\n").encode("utf-8"))
                    else:
                        s.sendall((self.headers['x-auth-token'] + "\n").encode("utf-8"))
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

    def __get_udp_socket(self):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if ":" not in self.config.server:
                if "/" not in self.config.server:
                    server = self.config.server
                else:
                    server = self.config.server.split("/")[0]
            else:
                server = self.config.server.split(":")[0]

            response = requests.get(self.config.server + SOCKET_URL, headers=self.headers)
            if response.status_code == 200:
                port = int(response.text)

                s.connect((server, port))
                return s
        except:
            print("Connection refused")
        return None

    def __reset_socket(self,protocol):
        if protocol is None or protocol.upper() == "TCP":
            if self.config.client_tcp_socket is not None:
                self.config.client_tcp_socket.close()
                self.config.client_tcp_socket = None
        else:
            if self.config.client_udp_socket is not None:
                self.config.client_udp_socket.close()
                self.config.client_udp_socket = None

    def __print__(text):
        print(text)
        sys.stdout.flush()

