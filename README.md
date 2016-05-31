# simple-notebook-server

simple-notebook-server provides a very simple implementation of an iPython notebook accessible vis websocket.  
The websocket server actions are:
* listen to incoming connections  
* executes any Python code it receives  
* intercept the output  
* send the output back to the client  
<br/>

Features of simple-notebook-server:  
* the execution context between requests is saved so that for instance if a request defines a variable, the variable is defined and accessible during all the following requests (in the same session);   
* execution of Python code is serialised so that in any moment the server executes only and only one request (per client).  

## Installation
It is recommended to use virtualenv to install all the required dependencies.  
Once the virtualenv has been created, run:
```bash
(simple-notebook-server)Red:simple-notebook-server fix$ pip install -r requirements.txt
```

After that run simple-notebook-server:  
```bash
(simple-notebook-server)Red:simple-notebook-server fix$ python server.py --log DEBUG
2016-05-31 11:00:40+0100 [-] Log opened.
2016-05-31 11:00:40+0100 [-] WebSocketServerFactory starting on 3001
2016-05-31 11:00:40+0100 [-] Starting factory <autobahn.twisted.websocket.WebSocketServerFactory object at 0x104ee4390>
```

To test simple-notebook-server:  
* open index.html with a web browser  
* click on the Connect button  
* try and execute some Python code  

## Message format
The server expects to receive the following JSON document:  
```javascript
{
  "code": "print('test')\nfor i in range(3)\nprint i"
}
```

The client will receive JSON document in this format:
```javascript
{
  "output": "test\n1\n2\n3\n"
}
```
