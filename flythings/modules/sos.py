import json
from enum import Enum
import requests
from flythings.base_client import BaseClient
from flythings.paths import PUBLISH_INFRASTRUCTURE, PUBLISH_INFRASTRUCTURE_METADATA, PUBLISH_INFRASTRUCTURE_SIMPLE, \
    DEVICE_METADATA_URL


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


class SosModule(BaseClient):
    def __init__(self, config):
        super().__init__(config)


    def save_text_metadata(self, key, value, foi=None):
        if foi is None or foi == '':
            foi = self.config.foi
        message = {'key': key.upper(), 'value': value, 'type': 'TEXT'}
        json_payload = json.dumps(message)
        response = requests.put(self.config.server + DEVICE_METADATA_URL + '/identifier/' + foi, json_payload,
                                headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
        return response.status_code

    def save_date_metadata(self,key, value, foi=None):
        if foi is None or foi == '':
            foi = self.config.foi
        message = {'key': key.upper(), 'value': value, 'type': 'DATE'}
        json_payload = json.dumps(message)
        response = requests.put(self.config.server + DEVICE_METADATA_URL + '/identifier/' + foi, json_payload,
                                headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
        return response.status_code

    @staticmethod
    def get_text_metadata(key, value, tag_id=None):
        metadata = {'key': key.upper(), 'value': value, 'tagId': tag_id, 'type': 'TEXT'}
        return metadata

    @staticmethod
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

    @staticmethod
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

    def save_infrastructure(self, infrastructure, id=None):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None, None
        if id is not None:
            infrastructure.id = id
        json_payload = json.dumps(infrastructure)
        response = requests.post(self.config.server + PUBLISH_INFRASTRUCTURE_METADATA,
                                 json_payload, headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
            return response.status_code, None
        return response.status_code, json.loads(response.text)

    def save_infrastructure_with_metadata(self, infrastructure, id=None):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None, None
        if id is not None:
            infrastructure.id = id
        json_payload = json.dumps(infrastructure)
        response = requests.post(self.config.server + PUBLISH_INFRASTRUCTURE_METADATA,
                                 json_payload, headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
            return response.status_code, None
        return response.status_code, json.loads(response.text)

    def save_infrastructure_without_override_fois(self, infrastructure, id=None):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None, None
        if id is not None:
            infrastructure.id = id
        json_payload = json.dumps(infrastructure)
        response = requests.post(self.config.server + PUBLISH_INFRASTRUCTURE_SIMPLE,
                                 json_payload, headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
            return response.status_code, None
        return response.status_code, json.loads(response.text)

    def link_device_to_infrastructure(self,infrastructure_tree, foi_identifier):
        if self.headers['x-auth-token'] == '':
            print('NoAuthenticationError')
            return None
        if foi_identifier is None:
            print('foi_identifier is None')
            return None
        json_payload = json.dumps(infrastructure_tree)
        response = requests.put(
            self.config.server + PUBLISH_INFRASTRUCTURE + "/link/featureofinterest/" + foi_identifier,
            json_payload, headers=self.headers, timeout=self.config.timeout)
        if response.status_code >= 400:
            print(response.text)
        return response.status_code
