# Sos Module

[Getting Started](https://github.com/flythings/python)

### Index

* [Save Text Metadata](#save_text_metadata)
* [Save Date Metadata](#save_date_metadata)
* [Get Infrastructure](#get_infrastructure)
* [Get Infrastructure with metadata](#get_infrastructure_withmetadata)
* [Save Infrastructure](#save_infrastructure)
* [Save Infrastructure with Metadata](#save_infrastructure_withmetadata)
* [Link Device to Infrastructure](#link_device_to_infrastructure)

## Module Methods

- <a name="save_text_metadata"></a>**save_text_metadata**(String key, String value, String foi_identifier)    
  **Description**: saves text metadata for a device.   
  **Params**:
    - key: (Mandatory) Key of the metadata on this format ("Category"."Name").
    - value: (Mandatory) Value of the metadata.
    - foi_identifier: (Optional) identifier of the device.

  **Return**: Returns the status code of the request:
    - status code 200 indicates that was correct insertion.

  **Examples**:
    * Adds a simple observation without configuration File.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        fly.save_text_metadata("CATEGORIA.NOMBRE", "valor", "database")    
    ```

- <a name="save_date_metadata"></a>**save_date_metadata**(String key, String value, String foi_identifier)    
  **Description**: saves text metadata for a device.   
  **Params**:
    - key: (Mandatory) Key of the metadata on this format ("Category"."Name").
    - value: (Mandatory) Value of the metadata in date format (17/02/2022) (17:00:00 17/02/2022).
    - foi_identifier: (Optional) identifier of the device.

  **Return**: Returns the status code of the request:
    - status code 200 indicates that was correct insertion.

  **Examples**:
    * Adds a simple observation without configuration File.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        fly.save_text_metadata("CATEGORIA.NOMBRE", "17/02/2022", "database")    
    ```

- <a name="get_text_metadata"></a>**get_text_metadata**(String key, String value, Long tag_id)    
  **Description**: get a text metadata object for infrastructure metadata.   
  **Params**:
    - key: (Mandatory) Key of the metadata on this format ("Category"."Name").
    - value: (Mandatory) Value of the metadata in text format.
    - tag_id: (Optional) identifier of the infrastructure.

  **Return**: Returns the metadata object.

  **Examples**:
    * Get metadata without configuration File.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        text_metadata_list = []
        text_metadata_list.append(flythings.get_text_metadata('.METADATA_TEST', 'test-metadata'))   
    ```

- <a name="get_infrastructure"></a>**get_infrastructure**(String name, String type, Geom geom, SamplingFeatureType
  geom_type, List<Long> fois, List<Metadata> text_metadata_list)    
  **Description**: get infrastructure object.   
  **Params**:
    - name: (Mandatory) Key of the metadata on this format ("Category"."Name").
    - type: (Mandatory) type level of the infrastructure.
    - geom: (Optional) geom position of the infrastructure.
    - geom_type: (Optional) geomType position type of the infrastructure.
    - fois: (Optional) list of foiIds of the infrastructure.

  **Return**: Returns the infrastructure object.

  **Examples**:
    * Get infrastructure without configuration File.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        infra = flythings.get_infrastructure_withmetadata('test-infrastructure', 'MILKCHAIN_FARM', None, None, None)
    ```

- <a name="get_infrastructure_withmetadata"></a>**get_infrastructure_withmetadata**(String name, String type, Geom geom,
  SamplingFeatureType geom_type, List<Long> fois, List<Metadata> text_metadata_list)    
  **Description**: get a text metadata object for infrastructure metadata.   
  **Params**:
    - name: (Mandatory) Key of the metadata on this format ("Category"."Name").
    - type: (Mandatory) type level of the infrastructure.
    - geom: (Optional) geom position of the infrastructure.
    - geom_type: (Optional) geomType position type of the infrastructure.
    - fois: (Optional) list of foiIds of the infrastructure.
    - text_metadata_list: (Optional) list of text metadata of the infrastructure.

  **Return**: Returns the infrastructure object.

  **Examples**:
    * Get infrastructure without configuration File.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        text_metadata_list = []
        text_metadata_list.append(flythings.get_text_metadata('.METADATA_TEST', 'test-metadata'))
        infra = flythings.get_infrastructure_withmetadata('test-infrastructure', 'MILKCHAIN_FARM', None, None, None, text_metadata_list)
   
    ```

- <a name="save_infrastructure"></a>**save_infrastructure**(Infrastructure infrastructure, Long featureTagId)    
  **Description**: saves infrastructure.
  **Params**:
    - infrastructure: (Mandatory) Infrastructure object obtained using get_infrastructure.
    - id: (Optional) Infrastructure id of the infrastructure.

  **Return**: Returns the status code of the request.

  **Examples**:
    * Update infrastructure.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        infra = flythings.get_infrastructure('test-infrastructure', 'MILKCHAIN_FARM', None, None, None)
        updated = flythings.save_infrastructure(infra)
    ```

- <a name="save_infrastructure_withmetadata"></a>**save_infrastructure_withmetadata**(Infrastructure infrastructure, Long featureTagId)    
  **Description**: saves infrastructure with metadata.   
  **Params**:
    - infrastructure: (Mandatory) Infrastructure object obtained using get_infrastructure_withmetadata.
    - id: (Optional) Infrastructure id of the infrastructure.

  **Return**: Returns the status code of the request.

  **Examples**:
    * Update infrastructure.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        text_metadata_list = []
        text_metadata_list.append(flythings.get_text_metadata('.METADATA_TEST', 'test-metadata'))
        infra = flythings.get_infrastructure_withmetadata('test-infrastructure', 'MILKCHAIN_FARM', None, None, None, text_metadata_list)
        updated = flythings.save_infrastructure_withmetadata(infra)
    ```
  

- <a name="link_device_to_infrastructure"></a>**link_device_to_infrastructure**(InfrastructureTree infrastructureTree, String device_identifier)    
  **Description**: Links device to infrastructure.   
  **Params**:
    - infrastructure_tree: (Mandatory) Infrastructure object tree.
    - device_identifier: (Mandatory) Device identifier.

  **Return**: Returns the status code of the request.

  **Examples**:
    * Link device to infrastructure with only parent level.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        infrastructure_tree = {'name': 'level1', 'type':'TAG_FIRST_LEVEL'}
        updated = flythings.link_device_to_infrastructure(infrastructure_tree, 'TestDeviceIdentifier')
    ```
    * Link device to infrastructure with multiple levels.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        infrastructure_tree = {'name': 'level1', 'type':'TAG_FIRST_LEVEL',
          'child':{'name': 'level2', 'type': 'TAG_SECOND_LEVEL'}
        }
        updated = flythings.link_device_to_infrastructure(infrastructure_tree, 'TestDeviceIdentifier')
    ```