import json
import time
from datetime import timedelta, datetime
import requests
from flythings.base_client import BaseClient
from flythings.modules.insertion import InsertionModule
from flythings.paths import PUBLISH_PREDICTION_MULTIPLE_URL, GET_PREDICTIONS_URL, PUBLISH_PREDICTION_SINGLE_URL


class PredictionModule(BaseClient):
    def __init__(self, config):
        super().__init__(config)

    def send_predictions(self, values):
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
                response = self.__send_predictions(aux_values)
                if response >= 400:
                    return response
                i += 1000
        else:
            response = self.__send_predictions(values)
        return response

    def __send_predictions(self, values):
        response = None
        try:
            response = requests.put(self.config.server + PUBLISH_PREDICTION_MULTIPLE_URL,
                                    data=json.dumps({'predictions': values}),
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

    def search_prediction(
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
        r = requests.post(self.config.server + GET_PREDICTIONS_URL, data=json.dumps(message), headers=self.headers,
                          timeout=self.config.timeout)
        if r.status_code == 200:
            list = r.json()[0]['data']
            return_list = []
            for elem in list:
                return_list.append({'value': elem[1], 'time': elem[0]})
            return return_list
        else:
            print(r.text)


    def send_prediction(
        self,
        insertion_module: InsertionModule,
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

        message = insertion_module.get_observation(value, property, uom, ts, geom, procedure, foi, device_type, foi_name)
        json_payload = json.dumps(message)
        response = requests.put(self.config.server + PUBLISH_PREDICTION_SINGLE_URL, json_payload, headers=self.headers,
                                timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
        return response.status_code

