
# [FlyThings Client](http://flythings.io) - developed by [ITG](http://www.itg.es)  
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
  
### Module Methods  
  
- setServer(String server)    
    **Description**: Sets the server to which the requests will be sent.      
    **Return**: Returns a string representing the server.     
      
- setDevice(String device)    
    **Description**: Sets the device of the observation.    
    **Return**: Returns a string representing the device.    
      
- setSensor(String sensor)    
    **Description**: Sets the sensor of the observation.    
    **Return**: Returns a string representing the sensor.     
      
- setToken(String token)   
    **Description**: Sets the token to authenticate into the server.    
    **Return**: Returns a string representing the token.  
    
- setCustomHeader(String header, String header_value)  
    **Description**: Sets a custom header for server requests.   
    **Return**: Returns a string representing the header.  
  
- setTimeout(int timeout)     
    **Description**: Sets the timeout value in seconds to the server requests.    
    **Return**: Returns a integer representing the timeout.  
      
- login(String user, String password)    
    **Description**: Authenticate against the server.     
    **Return**: Returns a string representing the token.    
  
- sendObservation([String,Double,GeomObj,Boolean] value, String property, String uom, Timestamp time, GeomObj geom, String procedure, String foi)    
    **Description**: sends a observation to the server.    
    **Params**:    
      - value: (Mandatory) Value to insert in the observation.    
      - property: (Mandatory) Property of the observation.    
      - uom: (Optional) unit of the measurement  
      - time: (Optional) Timestamp when the measurement was taken.    
      - geom: (Optional)  Geom object of the observation.    
      - procedure: (Optional) Sensor of the observation.    
      - foi:  (Optional) Device of the observation.      
    **Return**: Returns a message containing:      
    ```{OK: FULL INSERTION}```    
    if the observation was inserted, otherwise returns message error:    
    ```{ type: Error, message: Message Error in text format}```    
    **Examples**:    
      
    * Adds a simple observation without configuration File.  
    ```PYTHON  
        import flythings    
        flythings.setServer("beta.flythings.io/api")    
        flythings.login("<your username>","<your password>")    
        flythings.sendObservation(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Adds a simple observation having server, sensor and device in the Configuration File.  
    ```PYTHON  
        import flythings     
        flythings.login("<your username>","<your password>")    
        flythings.sendObservation(20,"prueba")    
    ```  
    * Adds a simple observation having all the parameters of the configuration File.  
    ```PYTHON  
        import flythings     
        flythings.login("<your username>","<your password>")    
        flythings.sendObservation(20,"prueba")    
    ```    
    * Adds a simple observation with timezone.  
    ```PYTHON  
    import flythings      
    flythings.setServer("beta.flythings.io/api")      
    flythings.login("<your username>","<your password>")     
    flythings.sendObservation(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Adds a simple observation with uom.  
    ```PYTHON  
    import flythings      
    flythings.setServer("beta.flythings.io/api")      
    flythings.login("<your username>","<your password>")     
    flythings.sendObservation(20,"prueba","m",None,None,"procedure","foi")    
    ```    
    * Adds a simple observation with Geom.  
    ```PYTHON  
    import flythings      
    flythings.setServer("beta.flythings.io/api")      
    flythings.login("<your username>","<your password>")     
    auxGeom = {  
        "type": "Point",  
        "crs": "4326",  
        "coordinates": [-19.323204,27.611808]  
    }  
    flythings.sendObservation(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  
  
- getObservation((String,Double,GeomObj,Boolean) value, String property, String uom, Timestamp time, GeomObj geom, String procedure, String foi)    
    **Description**: creates a observation Object.    
    **Params**:    
      - value: (Mandatory) Value to insert in the observation.    
      - property: (Mandatory) Property of the observation.    
      - uom: (Optional) unit of the measurement    
      - time: (Optional) Timestamp when the measurement was taken.    
      - geom: (Optional)  Geom object of the observation.    
      - procedure: (Optional) Sensor of the observation.    
      - foi:  (Optional) Device of the observation.    
    **Return**: Returns the observation object created.    
    **Examples**:    
      
    * Generates a simple observation without configuration File.  
    ```PYTHON  
        import flythings    
        flythings.setServer("beta.flythings.io/api")    
        flythings.login("<your username>","<your password>")    
        flythings.getObservation(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Generates a simple observation having server, sensor and device in the Configuration File.  
    ```PYTHON  
        import flythings     
        flythings.login("<your username>","<your password>")    
        flythings.getObservation(20,"prueba")    
    ```  
    * Generates a simple observation having all the parameters of the configuration File.  
    ```PYTHON  
        import flythings     
        flythings.login("<your username>","<your password>")    
        flythings.getObservation(20,"prueba")    
    ```    
    * Generates simple observation with timezone.  
    ```PYTHON  
    import flythings      
    flythings.setServer("beta.flythings.io/api")      
    flythings.login("<your username>","<your password>")     
    flythings.getObservation(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Generates simple observation with uom.  
    ```PYTHON  
    import flythings      
    flythings.setServer("beta.flythings.io/api")      
    flythings.login("<your username>","<your password>")     
    flythings.getObservation(20,"prueba","m",None,None,"procedure","foi")  
    ```  
    * Generates simple observation with Geom.  
    ```PYTHON  
    import flythings      
    flythings.setServer("beta.flythings.io/api")      
    flythings.login("<your username>","<your password>")     
    auxGeom = {  
        "type": "Point",  
        "crs": "4326",  
        "coordinates": [-19.323204,27.611808]  
    }  
    flythings.getObservation(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  
      
- sendObservations([observationObject] observations)    
    **Description**: sends multiple observations.      
    **Params**:    
      - observations: (Mandatory) list of observationObject to insert.     
   **Return**: Returns a message containing:    
    ```{OK: FULL INSERTION}```    
    if the observation was inserted, otherwise returns message error:    
    ```{ type: Error, message: Message Error in text format}```    
    **Examples**:  
   * Multiple Insert  
    ```PYTHON  
        import flythings     
        flythings.login("<your username>","<your password>")    
        observations = []  
        observations.append(flythings.getObservation(40,'probando'))  
        observations.append(flythings.getObservation(40,'multiple'))  
        flythingsClient.sendObservations(observations)  
    ``` 
- sendRecord(int seriesId, RecordObservation observations)    
    **Description**: sends a record to the service.      
    **Params**:    
      - seriesId: (Mandatory) The seriesId which represents the series.
      - observations: (Mandatory) Observations to insert into the series.
	      Here you can see a expmple of RecordObservation object:
       ```  [{value:5.0, time:1540453750781}, {value:2.5, time:1540453850781}]```
   **Return**: Returns a pair containing:
    ```(200, {OK: FULL INSERTION})```
    if the observation was inserted, otherwise returns message error:
    ```(400 , { type: Error, message: Message Error in text format})```
   **Examples**:
	 * Insert  record
	```PYTHON
       import flythings
       flythings.login("<your username>","<your password>")
       observations = []
       observations.append({value:5.0, time:1540453750781})
       observations.append({value:2.5, time:1540453850781})
       flythingsClient.sendRecord(947, observations)
	```
 - findSeries(String foi, String procedure, String observable_property)
   **Description**: finds a series by foi, procedure and observable_property.
   **Params**:
	    - foi: (Mandatory) String representing the foi name.
	    - procedure: (Mandatory)  String representing the procedure name.
	    - observable_property:  (Mandatory) String representing the observable property name.
   **Return**: Returns a series object.
   if request wasn´t succesfully :  Returns none .
   **Examples**:
	 * Search data of a series.
   ```PYTHON
       import flythings
       flythings.login("<your username>","<your password>")
       series = flythings.findSeries('foi', 'procedure', 'observable_property')
   ```

- search(Long series, Timestamp start, Timestamp end, String aggrupation, String aggrupationType)
    **Description**: retrieves the observation values of a series in a specified range of time.
    **Params**:
      - series: (Mandatory) SeriesId of the information we want.
      - start: (Optional)  Default (Last week),  Start value of the timerange.
      - end:  (Optional)Default (today), End value of the timerange.
      - aggrupation: (Optional) Aggrupation Type, could be (HOURLY,DAILY,MONTHLY,ANNUALLY)
      - aggrupationType:  (Optional)  Aggrupation Operation, could be (FIRST,MIN,MEAN,SUM,MAX,LAST)
    **Return**: Returns a message containing:
    ```{OK: FULL INSERTION}```
    if the observation was inserted, otherwise returns message error:
    ```{ type: Error, message: Message Error in text format}```
    **Examples**:

   * Search data of a series.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>")
        flythings.search(947,1495643746000,1496248546000)
    ```

    * Search data of a series without start and end date.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>")
        flythings.search(40)
    ```
     * Search data of a series without end date.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>")
        flythings.search(40,1495787136953)
    ```
- sendSocket(Long seriesId, Double value, Long timestamp, String protocol)
    **Description**: sends observation using a TCP socket connection.
    **Params**:
      - seriesId: (Mandatory) Identifier of the series of the device.
      - value: (Mandatory)  Value of the sample.
      - timestamp:  (Mandatory) Timestamp of the sample.
      - protocol: (Optional) Transport protocol TCP (default) or UDP
    **Return**: None if all was correct, otherwise returns message error:
    ```ERROR CONNECTING WITH WEBSOCKET```
    **Examples**:

   * Search data of a series.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        flythings.sendSocket("<seriesId>", <value>, <timestamp>, "<protocol>")
    ```

- registerAction(String name, Function callback, String foi, ActionDataTypes parameterType)
    **Description**: registers an action with the server, when the action is later run by the web client the callback is executed.
    **Params**:
      - name: (Mandatory) Identifier of the action..
      - callback: (Mandatory) Function that executes when the action is triggered.
      - foi:  (Optional) This parameter is optional if it was already set with the setDevice method otherwise is mandatory.
      - parameterType: (Optional) Especifies the parameter type of the callback if any.
    **Return**: True if all was correct, otherwise False.
    ```NoAuthenticationError```
    ```NoDeviceError```
    ```NoProcedureError```
    **Examples**:

   * Search data of a series.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerAction("<name>", test, foi="<device>", parameterType=flythings.ActionDataTypes.TEXT)
    ```

- registerActionForSeries(String name, String observableProperty, String unit, Function callback, String foi, String procedure, ActionDataTypes parameterType)
    **Description**: registers an action with the server, when the action is later run by the web client the callback is executed.
    **Params**:
      - name: (Mandatory) Identifier of the action.
      - observableProperty: (Mandatory) Observable property of the series.
      - unit: (Mandatory) Unit property of the series.
      - callback: (Mandatory) Function that executes when the action is demanded.
      - foi: (Optional) This parameter is optional if it was already set with the setDevice method otherwise is mandatory.
      - procedure: (Optional) This parameter is optional if it was already set with the setProcedure method otherwise is mandatory.
      - parameterType: (Optional) Especifies the parameter type of the callback if any.
    **Return**: True if all was correct, otherwise False.
    ```NoAuthenticationError```
    ```NoDeviceError```
    ```NoProcedureError```
    **Examples**:

   * Search data of a series.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerAction("<name>","<observableProperty", "<unit>", test, foi="<device>", procedure="<procedure>", parameterType=flythings.ActionDataTypes.TEXT)
    ```

- startActionListening()
    **Description**: Starts listening to the server waiting for an action to trigger. Is necessary that at least one action is registered.
    **Return**: None
    ```NoDeviceException```
    ```NoRegisteredActionExcetion```
    **Examples**:

   * Search data of a series.
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerAction("<name>", test, foi="<device>", flythings.ActionDataTypes.TEXT)
        flythings.startActionListening()
    ```

- stopActionListening()
    **Description**: Stop listening to the server for actions.
    **Return**: None.
    ```NoAuthenticationError```
    ```NoDeviceError```
    ```NoProcedureError```
    **Examples**:

   * Search data of a series.
    ```PYTHON
        import flythings, time
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerAction("<name>", test, foi="<device>", ActionDataTypes.TEXT)
        flythings.startActionListening()
        time.sleep(10)
        flythings.stopActionListening()
    ```

- ActionDataTypes
**Description**: Enumerated withe the allowed datatypes for the callbacks of the actions.
**Values**:
- ActionDataTypes.BOOLEAN: The callback will receive a boolean value from the server when the action is triggered.
- ActionDataTypes.FILE: The callback will receive a string representing the url where the file is when the action is triggered.
- ActionDataTypes.NUMBER: The callback will receive a number from the server when the action is triggered.
- ActionDataTypes.TEXT: The callback will receive a string from the server when the action is triggered.
- ActionDataTypes.ARRAY: The callback will receive a string array from the server when the action is triggered.
  
  
### Tests  
In the test folder, after fill in the Configuration.Properties file write on bash:  
  
```BASH  
    nosetests flythingsTest.py  
```  
([Nose python library is needed](http://nose.readthedocs.io/en/latest/))