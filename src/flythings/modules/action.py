import ast
import copy
import json
import socket
import time
from enum import Enum
from inspect import signature
from threading import Thread, Event
import requests
from flythings.base_client import BaseClient
from flythings.paths import ACTIONS_URL


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


class ActionModule(BaseClient):
    def __init__(self, config):
        super().__init__(config)
        self.thread = Thread(target=self.__send_socket_batch)

    def __register_action(
        self,
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
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None
        elif foi is None and self.config.foi is None:
            print('NoDeviceError')
            return None
        elif observable_property is not None and (self.config.procedure is None and procedure is None):
            print('NoProcedureError')
            return None
        try:
            payload = {
                "name": name,
                "featureOfInterest": self.config.foi if foi is None else foi,
                "parameterType": ActionDataTypes(parameter_type).name if parameter_type is not None else None
            }
            if observable_property is not None:
                payload["procedure"] = self.config.procedure if procedure is None else procedure
                payload["observableProperty"] = observable_property
            if unit is not None:
                payload["unit"] = unit
            if alias is not None:
                payload["alias"] = alias
            if action_options is not None and parameter_type.name == ActionDataTypes.SELECTOR.name:
                payload["actionOptions"] = action_options
            if json_template is not None:
                payload["jsonTemplate"] = json_template
            response = requests.post(self.config.server + ACTIONS_URL, data=json.dumps(payload), headers=self.headers)

            if response.status_code == 201:
                return True
            else:
                print(response.status_code)
        except Exception as e:
            print(e)
        return None

    def register_action_for_series(
        self,
        name,
        observable_property,
        unit,
        callback,
        foi=None,
        procedure=None,
        parameter_type=None,
        alias=None,
        action_options=None,
        json_template=None
    ):
        result = self.__register_action(name, parameter_type, foi, procedure, observable_property, unit, alias=alias,
                                   action_options=action_options, json_template=json_template)
        if result:

            if name not in self.callbacks:
                self.callbacks[name] = {'callback': callback, 'parameterType': parameter_type}
            else:
                return False
        return result is not None

    def register_action(self, name, callback, foi=None, parameter_type=None, alias=None, action_options=None,
                        json_template=None):
        result = self.__register_action(name, parameter_type, foi, alias=alias, action_options=action_options,
                                   json_template=json_template)
        if result:
            if name not in self.callbacks:
                self.callbacks[name] = {'callback': callback, 'parameterType': parameter_type}
            else:
                return False
        return result is not None

    def __action_socket_client(self, action_thread_stop, callbacks, foi):
        current_time = time.time()
        self.config.action_socket = None
        while not action_thread_stop.is_set():
            action_time = time.time()
            try:
                if self.config.action_socket is None:
                    self.config.action_socket = self.__get_tcp_socket(ACTIONS_URL)
                if self.config.action_socket is not None:
                    self.config.action_socket.settimeout(60.0)
                    data = self.config.action_socket.recv(1024)
                    decoded_data = data.decode("utf-8")
                    if decoded_data != '':
                        self.__parse_decoded_data(decoded_data, self.config.action_socket, foi)
                    try:
                        if action_time - current_time > 5:
                            self.config.action_socket.sendall("Ping\n".encode("utf-8"))
                            current_time = time.time()
                    except:
                        print("The server closed the connection!")
                        self.config.action_socket.close()
                        self.config.action_socket = None
                else:
                    print("Could not open Action socket, waiting 30 secs to retry")
                    time.sleep(30)
            except socket.timeout:
                print("timeout")
                self.config.action_socket.close()
                self.config.action_socket = None
                time.sleep(30)
                # __action_socket_client(actionThreadStop, callbacks, foi)
            except Exception as e:
                print(str(e))
                if str(e) != "'@PING@'":
                    print("INTERNAL_FAILURE")
                    if self.config.action_socket is not None:
                        self.config.action_socket.close()
                        self.config.action_socket = None
                    time.sleep(30)
                    # __action_socket_client(actionThreadStop, callbacks, foi)
        self.config.action_socket.close()

    def __parse_decoded_data(self, decoded_data, action_socket, foi):
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
                if command in self.callbacks:
                    try:
                        sig = signature(self.callbacks[command]['callback'])
                        if len(sig.parameters) == 0:
                            result = self.callbacks[command]['callback']()
                        elif len(sig.parameters) == 1:
                            result = self.callbacks[command]['callback'](
                                self.__cast_parameter(param, self.callbacks[command]['parameterType']))
                        elif len(sig.parameters) == 2:
                            result = self.callbacks[command]['callback'](
                                self.__cast_parameter(param, self.callbacks[command]['parameterType']), ts)
                        else:
                            result = self.callbacks[command]['callback'](
                                self.__cast_parameter(param, self.callbacks[command]['parameterType']), ts, action_log)
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
            return None
        except:
            return None

    def send_progress_action(self, message):
        try:
            if self.action_socket is None:
                raise Exception("Action Socket is not available")
            if message == 0 or isinstance(message, str):
                self.action_socket.sendall((str(message).replace('\n', '') + '\n').encode("utf-8"))
            else:
                self.action_socket.sendall("\n".encode("utf-8"))
        except Exception as e:
            print(e)
            print("ERROR SENDING PROGRESS ACTION")

    def start_action_listening(self, foi=None):
        if foi is not None and foi != '':
            f = foi
        else:
            f = self.config.foi
        if f is None or f == '':
            print("NoDeviceException")
            return None
        if not self.callbacks:
            print("NoRegisteredActionExcetion")
            return None
        self.action_thread_stop = Event()
        self.client_action_thread = Thread(target=self.__action_socket_client, args=(self.action_thread_stop, self.callbacks, f))
        self.client_action_thread.start()

    def stop_action_listening(self):
        if self.action_thread_stop:
            self.action_thread_stop.set()
        self.config.client_action_thread = None

    def __send_socket_batch(self,protocol=None):
        while True:
            if self.batch_enabled:
                client_socket = self.__get_socket(protocol)
                self.lock.acquire()
                acumulator = copy.deepcopy(self.config.real_time_acumulator)
                if client_socket is not None:
                    self.config.real_time_acumulator = {}
                    self.lock.release()
                    try:
                        values = acumulator.values()
                        for value in values:
                            json_payload = self.__acumulator_series_to_json(value)
                            client_socket.sendall(json_payload.encode("utf-8"))
                            try:
                                client_socket.recv(1024)
                            except socket.timeout:
                                print("Buffer was already empty")
                    except (socket.error, socket.timeout) as msg:
                        self.__print__("SOCKET ERROR:" + str(msg))
                        self.__reset_socket(protocol)
                else:
                    self.lock.release()
                    self.__print__("ERROR CONNECTING TO SOCKET")
            time.sleep(5)

