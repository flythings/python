
# [FlyThings Client](http://flythings.io) 
## Getting Started  
  
To use this client is necesary:  
*  Install [Python](https://www.python.org/)  
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
*  Example of configuration file  
```JSON  
    SERVER:beta.flythings.io/api  
    USER:<put your username here>  
    PASSWORD:<put your password here>  
    DEVICE:Python  
    SENSOR:Client  
    LOGIN_TYPE:USER or DEVICE
    TIMEOUT: 1000   
```  
  
You can also introduce this general properties using the library methods.  
  
### General Module Configuration Methods  
  
- **setServer**(String server)    
    **Description**: Sets the server to which the requests will be sent.      
    **Return**: Returns a string representing the server.     
      
- **setDevice**(String device)    
    **Description**: Sets the device of the observation.    
    **Return**: Returns a string representing the device.    
      
- **setSensor**(String sensor)    
    **Description**: Sets the sensor of the observation.    
    **Return**: Returns a string representing the sensor.     
      
- **setToken**(String token)   
    **Description**: Sets the token to authenticate into the server.    
    **Return**: Returns a string representing the token.  
    
- **setCustomHeader**(String header, String header_value)  
    **Description**: Sets a custom header for server requests.   
    **Return**: Returns a string representing the header.  
  
- **setTimeout**(int timeout)     
    **Description**: Sets the timeout value in seconds to the server requests.    
    **Return**: Returns a integer representing the timeout.  
      
- **login**(String user, String password)    
    **Description**: Authenticate against the server.     
    **Return**: Returns a string representing the token. 

 ### Modules documentation
- [InsertionModule](docs/InsertionModule.md)
- [RealTimeModule](docs/RealTimeModule.md)
- [ActionModule](docs/ActionModule.md)     
  
### Tests  
In the test folder, after fill in the Configuration.Properties file write on bash:  
  
```BASH  
    nosetests flythingsTest.py  
```  
([Nose python library is needed](http://nose.readthedocs.io/en/latest/))

## [License](LICENSE)
**Developed by [ITG](http://www.itg.es)**

 