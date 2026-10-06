import copy
import json
import socket
import time
from threading import Lock
from flythings.base_client import BaseClient

class RealTimeModule(BaseClient):
    def __init__(self, config):
        super().__init__(config)
        self.lock = Lock()

    def send_socket(self,series_id, value, timestamp, protocol=None):
        if self.batch_enabled:
            self.__save_batch_socket(series_id, value, timestamp)
        else:
            self.__send_socket(series_id, value, timestamp, protocol)

    def __save_batch_socket(self, series_id, value, timestamp):
        self.lock.acquire()
        if str(series_id) in self.real_time_acumulator:
            if int(time.time() * 1000) - \
                self.real_time_acumulator[str(series_id)][len(self.real_time_acumulator[str(series_id)]) - 1][
                    'timestamp'] >= self.batch_timeout:
                self.real_time_acumulator[str(series_id)].append({
                    'seriesId': series_id,
                    'timestamp': timestamp,
                    'value': value
                })
            else:
                self.lock.release()
                e_message = 'ERROR, DEVICE MUST WAIT AT LEAST 50ms BEFORE ACUMULATE ANOTHER OBSERVATION'
                self.__print__(e_message)
                return e_message
        else:
            self.real_time_acumulator[str(series_id)] = [{
                'seriesId': series_id,
                'timestamp': timestamp,
                'value': value
            }]
        self.lock.release()

    def __send_socket(self, series_id, value, timestamp, protocol=None):
        if self.last_real_time_timestamp is None or int(
            time.time() * 1000) - self.last_real_time_timestamp >= self.real_time_timeout:
            client_socket = self.__get_socket(protocol)

            if client_socket is not None:
                json_payload = self.__get_payload(series_id, value, timestamp, protocol)
                try:
                    client_socket.sendall(json_payload.encode("utf-8"))
                    try:
                        client_socket.recv(1024)
                    except socket.timeout:
                        print("Buffer was already empty")
                except socket.error as msg:
                    self.__reset_socket(protocol)
                    print(msg)
            else:
                print("ERROR CONNECTING TO SOCKET")
            print('CORRECT SENDED')
            self.last_real_time_timestamp = int(time.time() * 1000)
        else:
            e_message = 'ERROR, DEVICE MUST WAIT AT LEAST 1400ms BEFORE SEND A OBSERVATION FROM REALTIME'
            print(e_message)
            return e_message

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

    def __get_payload(self, series_id, value, timestamp, protocol):
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
                'X-AUTH-TOKEN': self.headers['x-auth-token'],
                'data': {

                    'seriesId': series_id,
                    'obs': [{
                        'seriesId': series_id,
                        'timestamp': timestamp,
                        'value': value
                    }]
                }
            })

