# [FlyThings Client](http://flythings.io) - developed by [ITG](http://www.itg.es)
## Getting Started

To use this client is necesary:
*	Install [Python](https://www.python.org/)
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

*  Example of configuration file
```JSON
    SERVER:beta.flythings.io/api
    USER:<put your username here>
    PASSWORD:<put your password here>
    DEVICE:Python
    SENSOR:Client
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
- search(Long series, Timestamp start, Timestamp end, String aggrupation, String aggrupationType)  
    **Description**: retrieves the observation values of a series in a specified range of time.     
    **Params**:    
      - series: (Mandatory) SeriesId of the information we want.  
      - start: (Mandatory)  Start value of the timerange.  
      - end:  (Mandatory) End value of the timerange.  
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




    
 
 

    
    


