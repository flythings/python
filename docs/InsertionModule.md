# Insertion Module
[Getting Started](https://github.com/flythings/python)
## Module Methods 
- **sendObservation**([String,Double,GeomObj,Boolean] value, String property, String uom, Timestamp time, GeomObj geom, String procedure, String foi)    
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
  
- **getObservation**((String,Double,GeomObj,Boolean) value, String property, String uom, Timestamp time, GeomObj geom, String procedure, String foi)    
    **Description**: creates a observation Object.    
    **Params**:    
      - value: (Mandatory) Value to insert in the observation.    
      - property: (Mandatory) Property of the observation.    
      - uom: (Optional) unit of the measurement    
      - time: (Optional) Timestamp when the measurement was taken.    
      - geom: (Optional)  Geom object of the observation.    
      - procedure: (Optional, Default configuration procedure) Sensor of the observation.    
      - foi:  (Optional, Default configuration foi) Device of the observation.    
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
      
- **sendObservations**([observationObject] observations)    
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
- **sendRecord**(int seriesId, RecordObservation observations)    
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
 - **findSeries**(String foi, String procedure, String observable_property)  
   **Description**: finds a series by foi, procedure and observable_property.  
   **Params**:
	    - foi: (Optional, Default configuration foi) String representing the foi name.  
	    - procedure: (Optional, Default configuration procedure)  String representing the procedure name.  
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

- **search**(Long series, Timestamp start, Timestamp end, String aggrupation, String aggrupationType)  
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

## [License](LICENSE)
**Developed by [ITG](http://www.itg.es)**