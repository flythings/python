# [FlyThings Client](http://flythings.io)

## Getting Started

To use this client is necesary:

* Install [Python](https://www.python.org/) (>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3*)
* Install [pip](https://pypi.python.org/pypi/pip?)
* To Install our library:

```BASH  
    $ pip install flythings   
````  

And now start to test the flythings clients.

## Documentation

### Configuration File

The general properties configuration in Configuration.properties:

* user: (Optional) user email or identifier to login on the system.
* password: (Optional) the user password to login, is not recommended use this configuration.
* server: (Optional, Default beta.flythings.io/api) configure the server url to insert the data.
* token: (Optional) the user token to send data into flythings plataform.
* device: (Optional) the device which sends data.
* sensor: (Optional) the sensor wich sends data.
* login_type: (Optional) type of login to use.
* timeout: (Optional) request timeout in seconds.
* authorization: (Optional) authorization token.
* Example of configuration file

```JSON  
    SERVER:beta.flythings.io/api  
    USER:<put your username here>  
    PASSWORD:<put your password here>  
    DEVICE:Python  
    SENSOR:Client  
    LOGIN_TYPE:USER or DEVICE
    TIMEOUT: 1000
    AUTHORIZATION: <put your token here>   
```  

To load the data from the file call this function:

- **load_data_by_file**(String file)      
  **Description**: Loads data from the file.        
  **Return**: Nothing.

**Examples**:

* Loads config data from a file.
  ```PYTHON import flythings as fly fly.loadDataByFile("/home/xxxx/configuration.properties")
  ```

You can also introduce this general properties using the library methods.

### General Module Configuration Methods

- **set_server**(String server)    
  **Description**: Sets the server to which the requests will be sent.      
  **Return**: Returns a string representing the server.

- **set_device**(String device, (Optional) object=None, always_update=False)   
  **Params**:
    - device: (Mandatory) Device name.
    - object: (Optional) Object with extra device params.
    - always_update: (Optional) Indicates if must send a request to create/update the device.  
      ```PYTHON
        object = {
          "type": "CUSTOM",
          "geom": {
          "type": "Point",
          "crs": "4326",
          "coordinates": [
          -19.323204, 27.611808
          ]
        } }
      ```                   
  **Description**: Sets the device of the observation. Uses a file named .foiCache to get a fast access to most used
  devices.      
  **Return**: Returns a string representing the device.

- **set_sensor**(String sensor)    
  **Description**: Sets the sensor of the observation.    
  **Return**: Returns a string representing the sensor.

- **set_token**(String token)   
  **Description**: Sets the x-auth-token to authenticate into the server.    
  **Return**: Returns a string representing the token.
  
- **set_worskapce**(Long workspace)   
  **Description**: Sets user workspace    
  **Return**: Returns the user workspace

- **set_custom_header**(String header, String header_value)  
  **Description**: Sets a custom header for server requests.   
  **Return**: Returns a string representing the header.

- **get_headers**(String header, String header_value)  
  **Description**: Return current headers.   
  **Return**:  Return current headers.

- **set_timeout**(int timeout)     
  **Description**: Sets the timeout value in seconds to the server requests.    
  **Return**: Returns an integer representing the timeout.

- **login**(String user, String password, String login_type ['USER' or 'DEVICE'])    
  **Description**: Authenticate against the server.     
  **Return**: Returns a string representing the token or None if login fails.
  
- **logout**() 
  **Description**: Logout against the server.     
  **Return**: Returns None.
  
- **set_authorization_token**(token)
  **Description**: Sets bearer token on authorization hearer.
  **Return**: returns the authorization header value.

### Modules documentation

- [InsertionModule](docs/InsertionModule.md)
- [RealTimeModule](docs/RealTimeModule.md)
- [ActionModule](docs/ActionModule.md)
- [PredictionModule](docs/PredictionModule.md)
- [SosModule](docs/SosModule.md)
- [UtilModule](docs/UtilModule.md)

### Tests

In the test folder, after fill in the Configuration.Properties file write on bash:

```BASH  
    nosetests flythingsTest.py  
```  

([Nose python library is needed](http://nose.readthedocs.io/en/latest/))

### Change log

- [Change log](changelog.md)

## [License](LICENSE)

**Developed by [ITG](http://www.itg.es)**

 