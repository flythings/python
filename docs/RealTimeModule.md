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

## [License](LICENSE)
**Developed by [ITG](http://www.itg.es)**
