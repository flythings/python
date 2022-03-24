# Prediction Module

[Getting Started](https://github.com/flythings/python)

### Index

* [Send Single Prediction](#send_prediction)
* [Send Predictions](#send_predictions.)
* [Search Predictions](#search_prediction)

## Module Methods

- <a name="send_prediction"></a>**send_prediction**([String,Double,GeomObj,Boolean] value, String property, String uom,
  Timestamp time, GeomObj geom, String procedure, String foi, String device_type, String foi_name)    
  **Description**: sends a prediction to the server.   
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
  if the prediction was inserted, otherwise returns message error:     
  ```{ type: Error, message: Message Error in text format}```    
  **Examples**:
    * Adds a simple prediction without configuration File.
    ```PYTHON  
        import flythings as fly   
        fly.setServer("api.flythings.io/api")    
        fly.login("<your username>","<your password>", "<login type>")
        fly.send_prediction(20,"prueba",None,None,None,"procedure","foi")    
    ```  
    * Adds a simple prediction having server, sensor and device in the Configuration File.
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>", "<login type>")    
        fly.send_prediction(20,"prueba")    
    ```  
    * Adds a simple prediction having all the parameters of the configuration File.
    ```PYTHON  
        import flythings as fly    
        fly.login("<your username>","<your password>", "<login type>")
        fly.send_prediction(20,"prueba")    
    ```    
    * Adds a simple prediction with timezone.
    ```PYTHON  
        import flythings as fly      
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        fly.send_prediction(20,"prueba",None,1495643746000,None,"procedure","foi")     
    ```    
    * Adds a simple prediction with uom.
    ```PYTHON  
        import flythings as fly     
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        fly.send_prediction(20,"prueba","m",None,None,"procedure","foi")    
    ```    
    * Adds a simple prediction with Geom.
    ```PYTHON  
        import flythings as fly      
        fly.setServer("api.flythings.io/api")      
        fly.login("<your username>","<your password>", "<login type>")     
        auxGeom = {  
                "type": "Point",  
                "crs": "4326",  
                "coordinates": [-19.323204,27.611808]  
        }  
        fly.send_prediction(20,"prueba",None,None,auxGeom,"procedure","foi")     
    ```  

- <a name="send_predictions"></a>**send_predictions**([observationObject] observations)    
  **Description**: sends multiple predictions.      
  **Params**:
    - predictions: (Mandatory) list of observationObject to insert.

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
        observations.append(fly.getObservation(40,'probando'))  
        observations.append(fly.getObservation(40,'multiple'))  
        fly.send_prediction(observations)  
    ```

- <a name="search_prediction"></a>**search_prediction**(Long series, Timestamp start, Timestamp end, String aggrupation,
  String aggrupation_type)  
  **Description**: retrieves the observation values of a series in a specified range of time.  
  **Params**:
    - series: (Mandatory) SeriesId of the information we want.
    - start: (Optional)  Default (Last week), Start value of the timerange.
    - end:  (Optional)Default (today), End value of the timerange.
    - aggrupation: (Optional) Aggrupation Type, could be (HOURLY,DAILY,MONTHLY,ANNUALLY)
    - aggrupation_type:  (Optional)  Aggrupation Operation, could be (FIRST,MIN,MEAN,SUM,MAX,LAST)

  **Return**: Returns a message containing:   
  ```{OK: FULL INSERTION}```    
  if the prediction was inserted, otherwise returns message error:    
  ```{ type: Error, message: Message Error in text format}```    
  **Examples**:
    * Search data of a series.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.search_prediction(947,1495643746000,1496248546000)
    ```
    * Search data of a series without start and end date.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.search_prediction(40)
    ```
    * Search data of a series without end date.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.search_prediction(40,1495787136953)
    ```

## [License](LICENSE)

**Developed by [ITG](http://www.itg.es)**
