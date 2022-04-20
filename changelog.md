## Change log

### 2.0.0
* Include predictions management methods.
* Refactor all methods to use _ instead of camel case.
* Include a method to set authorization token.
* Refactor send realtime messages to send samples on same format.
* Include batch_enabled as global variable.
* Include more action_types that Flythings Platform Allows.
* Posibilidad de actuaciones de tipo ongoing.

### 1.4.15
* Allow to save device metadata on text and date format.

### 1.4.14
* Include a flag to update always a featureOfInterest

### 1.4.13
* Include recv to clear buffer after send realtime data.

### 1.4.12
* Print response text after send observations to allow to view request errors.

### 1.4.11
* Include send alert device method
* Include send custom get request method
* Support HTTPs or HTTP

### 1.4.10
* Continue supporting Python2

### 1.4.9
* Fix findSeries was trying to load a json outside a try block.

### 1.4.8
* Fix send observations method was returning response if a exception was throw.

### 1.4.7
* Fix a error that action socket gets corrupted and wasn't able to detect that failure.

### 1.4.6
* Fix send record method.
* Include device_type and foi_name on observation construction.

### 1.4.5
* Fix failure setting timeout on TCP socket on socket creation
* Restore compatibility with Python2.7

### 1.4.4
* Include timeout on TCP sockets of 15 seconds.
* Improve code understandability.

### 1.4.3
* Fix pypy.org faulty update.

### 1.4.2
* Not append Unit if is none.
* Not reset the socket on ping exception.


### 1.4.1
* Fix socket never retry reconnect on service restart or turn off.


### 1.4.0
* Include getHeaders() to return current headers.
* Better documentation about action messages.
* Fix pypi.org not parsing property the .md files.
* Rename foi.txt cache foi file to .foiCache.


### 1.3.0
* Return None if login fails.  
* Allow actions to send String when the device wants to send a error to the server.  
* Refactor acumulateObss, now included on sendSocket if batch is enabled.  

### 1.2.3
* Remove pathlib dependency

### 1.2.2
* Checks if user has pathlib installed, if not, installs it.

### 1.2.1
* Checks if user has enum34 installed, if not, installs it.

### 1.2.0
* Include csv observation construction and insertion.
* Actions contains the action creation timestamp.
* Include action alias.
* Include action sequence diagram.

### 1.1.0
* Include batch to allow send multiple observations on real time.
* UpdateDevice() allows new device parameters and persist it on platform.
* Include changelog.