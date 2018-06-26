#!/usr/bin/python3           # This is server.py file
import socket                                         

# create a socket object
serversocket = socket.socket(
	        socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 53                         

# bind to the port
print(host) 
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)                                           

try:
    while True:
       clientsocket,addr = serversocket.accept()      
       msg = clientsocket.recv(1024)    
       print(msg)                                 
       clientsocket.close()    
except KeyboardInterrupt:
    print("interrupt")
finally:
    # clean up
    serversocket.close()


