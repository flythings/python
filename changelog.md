## Change log

### 2.2.4
* Update readme.
* Include alias on get infrastructure methods.
* Include set_authorization on config file.

### 2.2.3
* Allow to send json_template without need a series_action.

### 2.2.2
* Allow to send json_template on action register.

### 2.2.1
* Send observations and predictions on groups of 1000 on multiple insertion.

### 2.2.0
* Include get image observation by file, path, bytes or base64.
* Include logout method.
* Include set_server.
* Return response text on add infrastructure with or without metadata.
* Do nothing on set server if server is None.

### 2.1.1
* Fix SosModule documentation.

### 2.1.0
* Include save infrastructure.
* Include save infrastructure with metadata.
* Include link device to infrastructure.
* Remove create infrastructure with metadata.
* Remove update infrastructure with metadata.

### 2.0.2
* Include create infrastructure with metadata method.
* Include update infrastructure with metadata method.

### 2.0.1
* Include set x-auth-token to - on set_token().
* Fix authorization_token not working on action and realtime.
* Parse server hostname automatically on get_tcp_socket().
* Make set_server method more intelligent to autocomplete the required parts.
* Add metadata becomes save metadata which creates or updates metadata.

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