# Util Module

[Getting Started](https://github.com/flythings/python)

### Index

* [Get Request](#api_get_request)

## Module Methods

- <a name="api_get_request"></a>**api_get_request**([String] url)    
  **Description**: sends custom get request.   
  **Params**:
    - url: (Mandatory) Url of the request.

  **Return**: Returns a pair with request status code and request response:      
  ```200, {}```        
  **Examples**:
    * Sends a custom request.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.sendObservation(20,"prueba",None,None,None,"procedure","foi")    
        fly.api_get_request("/series/foi/procedure/prueba")    
    ```  

- <a name="send_device_alert"></a>**send_alert**([String] subject, [String] text)    
  **Description**: sends a device alert.   
  **Params**:
    - subject: (Mandatory) Subject of the message.
    - text: (Mandatory) Content of the message.

  **Return**: Returns a pair with request status code and request response:      
  ```200, {}```       
  **Examples**:
    * Sends a device request.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.send_alert("asunto", "contenido del mensaje")    
    ```  