# RealTime Module

[Getting Started](https://github.com/flythings/python)

### Index

* [Send Observation By Socket](#send_socket)
* [Set Batch State (enabled(dsabled)](#set_batch)

## Module Methods

- <a name="send_socket"></a>**send_socket**(Long seriesId, Double value, Long timestamp, String protocol)  
  **Description**: sends observation using a TCP socket connection if batch is not enabled, in this case the sending
  interval must be bigger than 1400ms, or adds a observation to the acumulator if batch is enabled, in this case the
  observation must have at least more than 50ms on timestamp than the last observation inserted with the same
  seriesId.    
  **Params**:
    - series_id: (Mandatory) Identifier of the series of the device.
    - value: (Mandatory)  Value of the sample.
    - timestamp:  (Mandatory) Timestamp of the sample.
    - protocol: (Optional) Transport protocol TCP (default) or UDP

  **Return**: None if all was correct, otherwise returns message error:  
  ```ERROR CONNECTING WITH WEBSOCKET```  
  ```ERROR, DEVICE MUST WAIT AT LEAST 50ms BEFORE ACUMULATE ANOTHER OBSERVATION```  
  ```ERROR, DEVICE MUST WAIT AT LEAST 1400ms BEFORE SEND A OBSERVATION FROM REALTIME```  
  **Examples**:
    * Send a observation using a socket.
    ```PYTHON
        import flythings as fly
        fly.login("<your username>","<your password>", "<login type>")
        fly.send_socket("<seriesId>", "<value>", "<timestamp>", "<protocol>")
    ```
    * adding a observation to the acumulator.
    ```PYTHON
        import flythings as fly
        import time
        fly.login("<your username>","<your password>", "<login type>")
        fly.set_batch_enabled(True)
        while True:
            fly.send_socket("<seriesId>", "<value>", "<timestamp>")
            time.sleep(0.05)
    ```

Also there is a process sending the observations on an acumulator to the service every 5 seconds.

- <a name="set_batch"></a>**set_batch_enabled**(Boolean active)  
  **Description**: activates or desactivates the batch process.  
  **Params**:
    - active: (Mandatory) Boolean.

  **Return**: None.  
  **Examples**:
    * activating the batch process.
    ```PYTHON
        import flythings as fly
        fly.set_batch_enabled(True)
    ```    

## [License](LICENSE)

**Developed by [ITG](http://www.itg.es)**
