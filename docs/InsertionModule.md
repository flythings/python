# Insertion Module
[Getting Started](https://github.com/flythings/python)

### Index
* [Send Single Observation](#send_observation)
* [Get Observation](#get_observation)
* [Get Observation CSV](#get_observation_csv)
* [Send Observations](#send_observations)
* [Send Observations CSV](#send_observations_csv)
* [Send Record](#send_record)
* [Find Series](#find_series)
* [Search](#search)

## Module Methods 
- <a name="send_observation"></a>**sendObservation**([String,Double,GeomObj,Boolean] value, String property, String uom, Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String foi_name)    
    **Description**: sends a observation to the server.   
    **Params**:    
    - value: (Mandatory) Value to insert in the observation.    
    - property: (Mandatory) Property of the observation.    
    - uom: (Optional) unit of the measurement  
    - time: (Optional) Timestamp when the measurement was taken.    
    - geom: (Optional)  Geom object of the observation.    
    - procedure: (Optional) Sensor of the observation.   
    - foi:  (Optional) Device of the observation. 
    - device_type:  (Optional, Default None) Type of the Device of the observation. 
    - foi_name:  (Optional, Default None) Name of the device of the observation. 
    
    **Return**: Returns a message containing:      
    ```{OK: FULL INSERTION}```     
    if the observation was inserted, otherwise returns message error:     
    ```{ type: Error, message: Message Error in text format}```    
    **Examples**:   
    * Adds a simple observation without configuration File.  
    ```PYTHON  
        import flythings as fly   
        fly.setServer("api.flythings.io/api")    
        fly.login("<your username>","<your password>")    
        fly.sendObservation(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Adds a simple observation having server, sensor and device in the Configuration File.  
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>")    
        fly.sendObservation(20,"prueba")    
    ```  
    * Adds a simple observation having all the parameters of the configuration File.  
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>")    
        fly.sendObservation(20,"prueba")    
    ```    
    * Adds a simple observation with timezone.  
    ```PYTHON  
        import flythings as fly      
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>")     
        fly.sendObservation(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Adds a simple observation with uom.  
    ```PYTHON  
        import flythings as fly     
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>")     
        fly.sendObservation(20,"prueba","m",None,None,"procedure","foi")    
    ```    
    * Adds a simple observation with Geom.  
    ```PYTHON  
        import flythings as fly      
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>")     
        auxGeom = {  
                "type": "Point",  
                "crs": "4326",  
                "coordinates": [-19.323204,27.611808]  
        }  
        fly.sendObservation(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  
  
- <a name="get_observation"></a>**getObservation**((String,Double,GeomObj,Boolean) value, String property, String uom, Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String foi_name)    
    **Description**: creates a observation Object.    
    **Params**:    
    - value: (Mandatory) Value to insert in the observation.    
    - property: (Mandatory) Property of the observation.    
    - uom: (Optional) unit of the measurement    
    - time: (Optional) Timestamp when the measurement was taken.    
    - geom: (Optional)  Geom object of the observation.    
    - procedure: (Optional, Default configuration procedure) Sensor of the observation.    
    - foi:  (Optional, Default configuration foi) Device of the observation.   
    - device_type:  (Optional, Default None) Type of the Device of the observation. 
    - foi_name:  (Optional, Default None) Name of the device of the observation. 
    
    **Return**: Returns the observation object created.    
    **Examples**:   
    * Generates a simple observation without configuration File.  
    ```PYTHON  
        import flythings as fly   
        fly.setServer("api.flythings.io/api")    
        fly.login("<your username>","<your password>")    
        fly.getObservation(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Generates a simple observation having server, sensor and device in the Configuration File.  
    ```PYTHON  
        import flythings as fly     
        fly.login("<your username>","<your password>")    
        fly.getObservation(20,"prueba")    
    ```  
    * Generates a simple observation having all the parameters of the configuration File.  
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>")    
        fly.getObservation(20,"prueba")    
    ```    
    * Generates simple observation with timezone.  
    ```PYTHON  
        import flythings as fly     
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>")     
        fly.getObservation(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Generates simple observation with uom.  
    ```PYTHON  
        import flythings as fly     
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>")     
        fly.getObservation(20,"prueba","m",None,None,"procedure","foi")  
    ```  
    * Generates simple observation with Geom.  
    ```PYTHON  
        import flythings as fly     
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>")     
        auxGeom = {  
                "type": "Point",  
                "crs": "4326",  
                "coordinates": [-19.323204,27.611808]  
        }  
        fly.getObservation(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  

- <a name="get_observation_csv"></a>**getObservationCSV**((String,Double,GeomObj,Boolean) value, Long serie, String uom, Timestamp ts, String property, String procedure, String foi)    
    **Description**: creates a observation CSV Object. If serie was inserted ignores foi, procedure and property.      
    **Params**:    
    - value: (Mandatory) Value to insert in the observation.    
    - serie: (Optional)  Serie of the observation.          
    - uom: (Optional) unit of the measurement    
    - ts: (Optional) Timestamp when the measurement was taken.    
    - property: (Optional) Property of the observation.    
    - procedure: (Optional, Default configuration procedure) Sensor of the observation.    
    - foi:  (Optional, Default configuration foi) Device of the observation.     
    
    **Return**: Returns the observation object created.    
    **Examples**:    
    * Generates a simple observation without configuration File.  
    ```PYTHON  
        import flythings as fly    
        fly.setServer("api.flythings.io/api")    
        fly.login("<your username>","<your password>")    
        csv = []    
        csv.append(flythings.getObservationCSV(20,series=123))    
        csv.append(flythings.getObservationCSV(25, uom='ºC', ts=int(time.time() * 1000), property='property', procedure='procedure', foi='foi'))        
    ```      
- <a name="send_observations"></a>**sendObservations**([observationObject] observations)    
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
        import flythings as fly     
        fly.login("<your username>","<your password>")    
        observations = []  
        observations.append(fly.getObservation(40,'probando'))  
        observations.append(fly.getObservation(40,'multiple'))  
        fly.sendObservations(observations)  
    ``` 
    
- <a name="send_observations_csv"></a>**sendObservationsCSV**([ObservationCSV] observations)    
  **Description**: sends a observation csv to the service.      
  **Params**:    
  - observations: (Mandatory) list of ObservationCSV to insert.  
  
  **Return**: Returns a pair containing:    
  ```(200, {OK: FULL INSERTION})```     
  if the observation was inserted, otherwise returns message error:    
  ```(400 , { type: Error, message: Message Error in text format})```     
  **Examples**:  
  * Sends multiple observations on csv format.   
  ```PYTHON  
        import flythings as fly    
        fly.setServer("api.flythings.io/api")    
        fly.login("<your username>","<your password>")    
        csv = []    
        csv.append(fly.getObservationCSV(20,series=123))    
        csv.append(fly.getObservationCSV(25, uom='ºC', ts=int(time.time() * 1000), property='property', procedure='procedure', foi='foi'))  
        print(fly.sendObservationsCSV(csv))
  ```      
    
- <a name="send_record"></a>**sendRecord**(int seriesId, RecordObservation observations)    
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
        import flythings as fly
        fly.login("<your username>","<your password>")
        observations = []
        observations.append({"value":5.0, "time":1540453750781})
        observations.append({"value":2.5, "time"":1540453850781})
        fly.sendRecord(947, observations)
    ```
	   
 - <a name="find_series"></a>**findSeries** (String foi, String procedure, String observable_property)    
   **Description**: finds a series by foi, procedure and observable_property.    
   **Params**:    
   - foi: (Optional, Default configuration foi) String representing the foi name.  
   - procedure: (Optional, Default configuration procedure)  String representing the procedure name.  
   - observable_property:  (Mandatory) String representing the observable property name.  
   
   **Return**: Returns a series object.  
   if request wasn´t succesfully :  Returns none.    
   **Examples**:  
   * Search data of a series.  
   ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>")
        series = fly.findSeries('foi', 'procedure', 'observable_property')
   ```

- <a name="search"></a>**search**(Long series, Timestamp start, Timestamp end, String aggrupation, String aggrupationType)  
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
        import flythings as fly
        fly.login("<your username>","<your password>")
        fly.search(947,1495643746000,1496248546000)
    ```
    * Search data of a series without start and end date.  
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>")
        fly.search(40)
    ```
     * Search data of a series without end date.  
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>")
        fly.search(40,1495787136953)
    ```

## [License](LICENSE)
**Developed by [ITG](http://www.itg.es)**
