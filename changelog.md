## Change log

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