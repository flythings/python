# Action Module 
[Getting Started](https://github.com/flythings/python)

## Action Types
- **ActionDataTypes**  
**Description**: Enumerated withe the allowed datatypes for the callbacks of the actions.  
**Values**:  
	- **ActionDataTypes.BOOLEAN**: The callback will receive a boolean value from the server when the action is triggered.  
	- **ActionDataTypes.FILE**: The callback will receive a string representing the url where the file is when the action is triggered.  
	- **ActionDataTypes.NUMBER**: The callback will receive a number from the server when the action is triggered.  
	- **ActionDataTypes.TEXT**: The callback will receive a string from the server when the action is triggered.  
	- **ActionDataTypes.ARRAY**: The callback will receive a string array from the server when the action is triggered.  

## Module Methods 

- **registerAction**(String name, Function callback, String foi, ActionDataTypes parameterType)  
    **Description**: registers an action with the server, when the action is later run by the web client the callback is executed.  
    **Params**:  
      - name: (Mandatory) Identifier of the action.  
      - callback: (Mandatory) Function that executes when the action is triggered.  
      - foi:  (Optional) This parameter is optional if it was already set with the setDevice method otherwise is mandatory.  
      - parameterType: (Optional, Default: None) Specifies the parameter type of the callback if any.  
    **Return**: True if all was correct, otherwise False.    
    ```NoAuthenticationError```  
    ```NoDeviceError```  
    ```NoProcedureError```  
    **Examples**:  

   * Register an action with the server.  
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerAction("<name>", test, foi="<device>", parameterType=flythings.ActionDataTypes.TEXT)
    ```

- **registerActionForSeries**(String name, String observableProperty, String unit, Function callback, String foi, String procedure, ActionDataTypes parameterType)  
    **Description**: registers an action with the server, when the action is later run by the web client the callback is executed.  
    **Params**:  
      - name: (Mandatory) Identifier of the action.  
      - observableProperty: (Mandatory) Observable property of the series.  
      - unit: (Mandatory) Unit property of the series.  
      - callback: (Mandatory) Function that executes when the action is demanded.  
      - foi: (Optional) This parameter is optional if it was already set with the setDevice method otherwise is mandatory.  
      - procedure: (Optional) This parameter is optional if it was already set with the setProcedure method otherwise is mandatory.  
      - parameterType: (Optional, Default: None) Specifies the parameter type of the callback if any.  
    **Return**: True if all was correct, otherwise False.    
    ```NoAuthenticationError```    
    ```NoDeviceError```  
    ```NoProcedureError```  
    **Examples**:  

   * Registers an action with the server.  
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerActionForSeries("<name>","<observableProperty", "<unit>", test, foi="<device>", procedure="<procedure>", parameterType=flythings.ActionDataTypes.TEXT)
    ```

- **startActionListening**()  
    **Description**: Starts listening to the server waiting for an action to trigger. Is necessary that at least one action is registered.  
    **Return**: None  
    ```NoDeviceException```  
    ```NoRegisteredActionExcetion```  
    **Examples**:  

   * Starts listening waiting for an action to trigger.  
    ```PYTHON
        import flythings
        flythings.login("<your username>","<your password>", "<login type>")
        def test(param):
          print(param)
        flythings.registerAction("<name>", test, foi="<device>", flythings.ActionDataTypes.TEXT)
        flythings.startActionListening()
        while(True):
            print("listening...")
            time.sleep(10)
    ```

- **stopActionListening**()  
    **Description**: Stop listening to the server for actions.  
    **Return**: None.  
    ```NoAuthenticationError```    
    ```NoDeviceError```    
    ```NoProcedureError```   
    **Examples**:  

   * Stop listening to the server for actions.  
    ```PYTHON
        import flythings, time
        flythings.login("<your username>","<your password>", "<login type>")
        listening = False
        def test(param):
          print(param)
          flythings.stopActionListening() #Stops listening when a action was triggered
          listening = False
        flythings.registerAction("<name>", test, foi="<device>", ActionDataTypes.TEXT)
        flythings.startActionListening()
        listening = True
        while(listening):
            print("listening...")
            time.sleep(10)
    ```  
## [License](LICENSE)
**Developed by [ITG](http://www.itg.es)**