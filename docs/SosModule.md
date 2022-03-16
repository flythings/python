# Sos Module
[Getting Started](https://github.com/flythings/python)

### Index
* [Save Text Metadata](#save_text_metadata)
* [Save Date Metadata](#save_date_metadata)

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
        fly.setServer("api.flythings.io/api")    
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
        fly.setServer("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        fly.save_text_metadata("CATEGORIA.NOMBRE", "17/02/2022", "database")    
    ```