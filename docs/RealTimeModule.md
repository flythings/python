# RealTime Module 
[Getting Started](https://github.com/flythings/python)

## Module Methods 

- **sendSocket**(Long seriesId, Double value, Long timestamp, String protocol)  
    **Description**: sends observation using a TCP socket connection.  
    **Params**:  
      - seriesId: (Mandatory) Identifier of the series of the device.  
      - value: (Mandatory)  Value of the sample.  
      - timestamp:  (Mandatory) Timestamp of the sample.  
      - protocol: (Optional) Transport protocol TCP (default) or UDP  
    **Return**: None if all was correct, otherwise returns message error:  
    ```ERROR CONNECTING WITH WEBSOCKET```  
    **Examples**:    

   * Send a observation using a socket.    
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        flythings.sendSocket("<seriesId>", <value>, <timestamp>, "<protocol>")
    ```

Also there is a process sending the observations on a acumulator to the service every 5 seconds.      
    
- **setBatchEnabled**(Boolean active)  
    **Description**: activates or desactivates the batch process.  
    **Params**:  
      - active: (Mandatory) Boolean.  
    **Return**: None.  
    **Examples**:    

   * activating the batch process.    
    ```PYTHON
        import flythings
        flythings.setBatchEnabled(True)
    ```    
    
    
- **acumulateObs**(Long seriesId, Double value, Long timestamp)  
    **Description**: adds a observation to the acumulator,
     the observation must have at least more than 50ms on timestamp than the last observation
     inserted with the same seriesId.   
    **Params**:  
      - seriesId: (Mandatory) Identifier of the series of the device.  
      - value: (Mandatory)  Value of the sample.  
      - timestamp:  (Mandatory) Timestamp of the sample.  
    **Return**:  None if all was correct, otherwise returns message error:  
    ```ERROR, DEVICE MUST WAIT AT LEAST 50ms BEFORE ACUMULATE ANOTHER OBSERVATION```    
    **Examples**:    

   * adding a observation to the acumulator.    
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        flythings.setBatchEnabled(True)
        while(True):
            flythings.acumulateObs("<seriesId>", <value>, <timestamp>)
            time.sleep(0.05)
    ```

## [License](LICENSE)
**Developed by [ITG](http://www.itg.es)**
