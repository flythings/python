# Insertion Module

[Getting Started](https://github.com/flythings/python)

### Index

* [Send Single Observation](#send_observation)
* [Get Observation](#get_observation)
* [Get Image Observation](#get_image_observation)
* [Get Image Bytes Observation](#get_image_bytes_observation)
* [Get Image Base64 Observation](#get_image_base64_observation)
* [Get Observation CSV](#get_observation_csv)
* [Send Observations](#send_observations)
* [Send Observations CSV](#send_observations_csv)
* [Send Record](#send_record)
* [Find Series](#find_series)
* [Search](#search)

## Module Methods

- <a name="send_observation"></a>**send_observation**([String,Double,GeomObj,Boolean] value, String property, String
  uom, Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String foi_name)    
  **Description**: sends an observation to the server.   
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
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        fly.send_observation(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Adds a simple observation having server, sensor and device in the Configuration File.
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.send_observation(20,"prueba")    
    ```  
    * Adds a simple observation having all the parameters of the configuration File.
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>", "<login type>")
        fly.send_observation(20,"prueba")    
    ```    
    * Adds a simple observation with timezone.
    ```PYTHON  
        import flythings as fly      
        fly.set_server("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        fly.send_observation(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Adds a simple observation with uom.
    ```PYTHON  
        import flythings as fly     
        fly.set_server("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        fly.send_observation(20,"prueba","m",None,None,"procedure","foi")    
    ```    
    * Adds a simple observation with Geom.
    ```PYTHON  
        import flythings as fly      
        fly.set_server("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        auxGeom = {  
                "type": "Point",  
                "crs": "4326",  
                "coordinates": [-19.323204,27.611808]  
        }  
        fly.send_observation(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  

- <a name="get_observation"></a>**get_observation**((String,Double,GeomObj,Boolean) value, String property, String uom,
  Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String foi_name)    
  **Description**: creates an observation Object.    
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
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.get_observation(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Generates a simple observation having server, sensor and device in the Configuration File.
    ```PYTHON  
        import flythings as fly     
        fly.login("<your username>","<your password>", "<login type>")    
        fly.get_observation(20,"prueba")    
    ```  
    * Generates a simple observation having all the parameters of the configuration File.
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.get_observation(20,"prueba")    
    ```    
    * Generates simple observation with timezone.
    ```PYTHON  
        import flythings as fly     
        fly.set_server("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        fly.get_observation(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Generates simple observation with uom.
    ```PYTHON  
        import flythings as fly     
        fly.set_server("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        fly.get_observation(20,"prueba","m",None,None,"procedure","foi")  
    ```  
    * Generates simple observation with Geom.
    ```PYTHON  
        import flythings as fly     
        fly.set_server("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        auxGeom = {  
                "type": "Point",  
                "crs": "4326",  
                "coordinates": [-19.323204,27.611808]  
        }  
        fly.get_observation(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  

- <a name="get_image_observation"></a>**get_image_observation**((String | File) file, String property, String format,
  String uom, Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String foi_name)    
  **Description**: creates an image observation Object.    
  **Params**:
    - file: (Mandatory) opened file or path of the file.
    - property: (Mandatory) Property of the observation.
    - format: (Optional) Format of the image.
    - uom: (Optional) unit of the measurement
    - time: (Optional) Timestamp when the measurement was taken.
    - geom: (Optional)  Geom object of the observation.
    - procedure: (Optional, Default configuration procedure) Sensor of the observation.
    - foi:  (Optional, Default configuration foi) Device of the observation.
    - device_type:  (Optional, Default None) Type of the Device of the observation.
    - foi_name:  (Optional, Default None) Name of the device of the observation.

  **Return**: Returns the observation object created.    
  **Examples**:
    * Generates a simple image observation by path.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.get_image_observation('McLaren-Racing-Gulf-Formula-1.jpg', 'ImageProperty', None, None,
                                   int(time.time() * 1000), None, 'default', 'ImageDevice'))    
    ```
    * Generates a simple image observation by file.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        file = open('McLaren-Racing-Gulf-Formula-1.jpg', "rb")    
        fly.get_image_observation(file, 'ImageProperty', 'jpg', None,
                                   int(time.time() * 1000), None, 'default', 'ImageDevice'))    
    ```

- <a name="get_image_bytes_observation"></a>**get_image_bytes_observation**(byte[] bytes, String property, String
  format, String uom, Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String
  foi_name)    
  **Description**: creates an image observation Object.    
  **Params**:
    - bytes: (Mandatory) opened file or path of the file.
    - property: (Mandatory) Property of the observation.
    - format: (Mandatory) Format of the image.
    - uom: (Optional) unit of the measurement
    - time: (Optional) Timestamp when the measurement was taken.
    - geom: (Optional)  Geom object of the observation.
    - procedure: (Optional, Default configuration procedure) Sensor of the observation.
    - foi:  (Optional, Default configuration foi) Device of the observation.
    - device_type:  (Optional, Default None) Type of the Device of the observation.
    - foi_name:  (Optional, Default None) Name of the device of the observation.

  **Return**: Returns the observation object created.    
  **Examples**:
    * Generates a simple image observation by bytes.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        file = open('McLaren-Racing-Gulf-Formula-1.jpg', "rb")
        bytes = file.read()
        observations.append(
            flythings.get_image_bytes_observation(bytes, 'ImageProperty', 'jpg', None,
                                           int(time.time() * 1000), None, 'default', 'ImageDevice'))   
    ```

- <a name="get_image_base64_observation"></a>**get_image_base64_observation**(String base64, String property, String
  format, String uom, Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String
  foi_name)    
  **Description**: creates an image observation Object.    
  **Params**:
    - base64: (Mandatory) base64 image.
    - property: (Mandatory) Property of the observation.
    - format: (Mandatory) Format of the image.
    - uom: (Optional) unit of the measurement
    - time: (Optional) Timestamp when the measurement was taken.
    - geom: (Optional)  Geom object of the observation.
    - procedure: (Optional, Default configuration procedure) Sensor of the observation.
    - foi:  (Optional, Default configuration foi) Device of the observation.
    - device_type:  (Optional, Default None) Type of the Device of the observation.
    - foi_name:  (Optional, Default None) Name of the device of the observation.

  **Return**: Returns the observation object created.    
  **Examples**:
    * Generates a simple image observation by base64.
    ```PYTHON  
        import flythings as fly   
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        file = open('McLaren-Racing-Gulf-Formula-1.jpg', "rb")
        b64 = base64.b64encode(file.read())
        observations.append(
            flythings.get_image_base64_observation(b64, 'ImageProperty', 'jpg', None,
                                           int(time.time() * 1000), None, 'default', 'ImageDevice')) 
    ```

- <a name="get_observation_csv"></a>**get_observation_csv**((String,Double,GeomObj,Boolean) value, Long serie, String
  uom, Timestamp ts, String property, String procedure, String foi)    
  **Description**: creates an observation CSV Object. If serie was inserted ignores foi, procedure and property.      
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
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")    
        csv = []    
        csv.append(flythings.get_observation_csv(20,series=123))    
        csv.append(flythings.get_observation_csv(25, uom='ºC', ts=int(time.time() * 1000), property='property', procedure='procedure', foi='foi'))        
    ```      
- <a name="send_observations"></a>**send_observations**([observationObject] observations)    
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
        fly.login("<your username>","<your password>", "<login type>")    
        observations = []  
        observations.append(fly.get_observation(40,'probando'))  
        observations.append(fly.get_observation(40,'multiple'))  
        fly.send_observations(observations)  
    ``` 

- <a name="send_observations_csv"></a>**send_observations_csv**([ObservationCSV] observations)    
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
        fly.set_server("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")    
        csv = []    
        csv.append(fly.get_observation_csv(20,series=123))    
        csv.append(fly.get_observation_csv(25, uom='ºC', ts=int(time.time() * 1000), property='property', procedure='procedure', foi='foi'))  
        print(fly.send_observations_csv(csv))
  ```      

- <a name="send_record"></a>**send_record**(int seriesId, RecordObservation observations)    
  **Description**: sends a record to the service.      
  **Params**:
    - series_id: (Mandatory) The seriesId which represents the series.
    - observations: (Mandatory) Observations to insert into the series.

  Here you can see an example of RecordObservation object:    
  ```  [{value:5.0, time:1540453750781}, {value:2.5, time:1540453850781}]```

  **Return**: Returns a pair containing:      
  ```(200, {OK: FULL INSERTION})```   
  if the observation was inserted, otherwise returns message error:    
  ```(400 , { type: Error, message: Message Error in text format})```   
  **Examples**:
    * Insert record
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        observations = []
        observations.append({"value":5.0, "time":1540453750781})
        observations.append({"value":2.5, "time":1540453850781})
        fly.send_record(947, observations)
    ```

- <a name="find_series"></a>**find_series** (String foi, String procedure, String observable_property)    
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
       fly.login("<your username>","<your password>", "<login type>")
       series = fly.find_series('foi', 'procedure', 'observable_property')
  ```

- <a name="search"></a>**search**(Long series, Timestamp start, Timestamp end, String aggrupation, String
  aggrupationType)  
  **Description**: retrieves the observation values of a series in a specified range of time.  
  **Params**:
    - series: (Mandatory) SeriesId of the information we want.
    - start: (Optional)  Default (Last week), Start value of the timerange.
    - end:  (Optional)Default (today), End value of the timerange.
    - aggrupation: (Optional) Aggrupation Type, could be (HOURLY,HOUR_OF_DAY, DAILY, DAY_OF_WEEK, MONTHLY, DAY_OF_MONTH, ANNUALLY, MONTH_OF_YEAR)
    - aggrupation_type:  (Optional)  Aggrupation Operation, could be (MIN, MAX, MEAN, SUM, LAST, FIRST, COUNT, STD)

  **Return**: Returns a message containing:   
  ```{OK: FULL INSERTION}```    
  if the observation was inserted, otherwise returns message error:    
  ```{ type: Error, message: Message Error in text format}```    
  **Examples**:
    * Search data of a series.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.search(947,1495643746000,1496248546000)
    ```
    * Search data of a series without start and end date.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.search(40)
    ```
    * Search data of a series without end date.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.search(40,1495787136953)
    ```

## [License](LICENSE)

**Developed by [ITG](http://www.itg.es)**
