import base64
import json
import time
import requests
from datetime import timedelta, datetime
from flythings.base_client import BaseClient
from flythings.paths import PUBLISH_MULTIPLE_URL, SERIES_URL, PUBLISH_RECORD_URL, PUBLISH_PLAIN_CSV_URL, \
    GET_OBSERVATIONS_URL, GET_LAST_VALUE_URL, PUBLISH_SINGLE_URL


class InsertionModule(BaseClient):
    def __init__(self, config):
        super().__init__(config)

    def send_observations(self, values):
        response = None
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return response
        if values is None:
            print('Values cannot be None')
            return response
        if len(values) > 1000:
            i = 0
            while i < len(values):
                aux_values = values[i:i + 1000]
                response = self.__send_observations(aux_values)
                if response >= 400:
                    return response
                i += 1000
        else:
            response = self.__send_observations(values)
        return response

    def __send_observations(self,values):
        response = None
        try:
            response = requests.put(self.config.server + PUBLISH_MULTIPLE_URL, data=json.dumps({'observations': values}),
                                    headers=self.headers, timeout=self.config.timeout)
        except Exception as e:
            print(e)
        if response is not None:
            if response.status_code >= 400:
                print(response.text)
            return response.status_code
        else:
            print("NO RESPONSE FROM SERVICE")
            return 502

    def get_observation(
        self,
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
            message['procedure'] = self.config.procedure
        if foi is not None and foi != '':
            message['foi'] = foi
        else:
            message['foi'] = self.config.foi
        if device_type is not None:
            message['deviceType'] = device_type
        if foi_name is not None:
            message['foiName'] = foi_name
        if force_type is not None:
            message['forceType'] = force_type
        return message

    def get_observation_csv(
        self,
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
                message += self.config.foi + ";"
            if procedure is not None:
                message += procedure + ";"
            else:
                message += self.config.procedure + ";"
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

    def find_series(self, foi=None, procedure=None, observable_property=None):
        if foi is None or foi == '':
            foi = self.config.foi
        if procedure is None or procedure == '':
            procedure = self.config.procedure
        if observable_property is None or observable_property == '':
            return "INSERT A OBSERVABLE PROPERTY"
        response = requests.get(self.config.server + SERIES_URL + foi + '/' + procedure + '/' + observable_property,
                                headers=self.headers, timeout=self.config.timeout)
        if response.status_code != 200:
            print("Error retrieving series: " + foi + "-" + procedure + "-" + observable_property)
            return None
        try:
            message = json.loads(response.content.decode("utf-8"))
            return message
        except:
            return None


    def send_record(self, serie_id, observations):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None
        if isinstance(observations, str):
            response = requests.put(self.config.server + PUBLISH_RECORD_URL + "/" + str(serie_id), observations,
                                    headers=self.headers)
        else:
            response = requests.put(self.config.server + PUBLISH_RECORD_URL + "/" + str(serie_id),
                                    data=json.dumps(observations), headers=self.headers)
        return response.status_code, response.content

    def send_observations_csv(self, values):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None
        response = requests.post(self.config.server + PUBLISH_PLAIN_CSV_URL, data=values, headers=self.headers,
                                 timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
        return response.status_code, response.content

    def search(
        self,
        series,
        start_date=None,
        end_date=None,
        aggrupation=None,
        aggrupation_type=None,
        as_incremental=False
    ):
        if self.headers['x-auth-token'] == '':
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
        r = requests.post(self.config.server + GET_OBSERVATIONS_URL, data=json.dumps(message), headers=self.headers,
                          timeout=self.config.timeout)
        if r.status_code == 200:
            list = r.json()[0]['data']
            return_list = []
            for elem in list:
                return_list.append({'value': elem[1], 'time': elem[0]})
            return return_list
        else:
            print(r.text)

    def get_last_observation_before_date(self, series_id, timestamp):
        if self.headers['x-auth-token'] == '':
            return 'NoAuthenticationError'

        r = requests.get(self.config.server + GET_LAST_VALUE_URL + f"/{series_id}/{timestamp}", headers=self.headers,
                         timeout=self.config.timeout)

        if r.status_code != 200 or len(r.content) == 0:
            print(r.text)
            return None

        result = r.json()
        return result['time'], result['value']

    def send_observation(
        self,
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

        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None
        message = self.get_observation(value, property, uom, ts, geom, procedure, foi, device_type, foi_name)
        json_payload = json.dumps(message)
        response = requests.put(self.config.server + PUBLISH_SINGLE_URL, json_payload, headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
        return response.status_code

    def get_image_observation(
        self,
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
            message['procedure'] = self.config.procedure
        if foi is not None and foi != '':
            message['foi'] = foi
        else:
            message['foi'] = self.config.foi
        if device_type is not None:
            message['deviceType'] = device_type
        if foi_name is not None:
            message['foiName'] = foi_name
        return message

    def get_image_bytes_observation(
        self,
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
            message['procedure'] = self.config.procedure
        if foi is not None and foi != '':
            message['foi'] = foi
        else:
            message['foi'] = self.config.foi
        if device_type is not None:
            message['deviceType'] = device_type
        if foi_name is not None:
            message['foiName'] = foi_name
        return message

    def get_image_base64_observation(
        self,
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
            message['procedure'] = self.config.procedure
        if foi is not None and foi != '':
            message['foi'] = foi
        else:
            message['foi'] = self.config.foi
        if device_type is not None:
            message['deviceType'] = device_type
        if foi_name is not None:
            message['foiName'] = foi_name
        return message



