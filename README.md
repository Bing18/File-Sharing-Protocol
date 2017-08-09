# File-Sharing-Application
It is a Application Level program to keep two separate directories synced, similar to Drop-box, using sockets.

## How to Start?
```
Usage: 
1. ' ./server.py '
2. ' ./client.py ' 
```
## Features
```
•The system will have 2 clients (acting as servers simultaneously) listening to the communication channel for requests and waiting to share files (avoiding collisions) using an application layer protocol.
• Each client has the ability to do the following:
	– Know the files present on each others machines in the designated shared folders.
	– Download files from the other shared folder.
• The system will periodically check for any changes made to the shared folders.
• File transfer will incorporate MD5 checksum to handle file transfer errors.
• The history of requests made by either clients will be logged at each of the clients respectively. 
```
