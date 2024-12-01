# cd C:\Users\hanna\CECS 327
# python "Echo Server.py"

# Isela's local IP: 
# 172.20.10.2
# 1026

import socket
from pymongo import MongoClient
import certifi
import getpass

#Mongo connection
try:
    password = getpass.getpass("Mongo db password: ")
    cluster = f"mongodb+srv://iselat5862:{password}@cluster0.goumq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(cluster, tlsCAFile=certifi.where())
    db = client['test']
    print("Mongo Collection names:")
    print(db.list_collection_names())
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# Creating a TCP socket
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Binding socket to IP address and port number
    myTCPSocket.bind(('0.0.0.0', 1024))#('localhost', 1024))

    # Listening for incoming client connections
    myTCPSocket.listen(5)
    print("Server is listening on port 1024...")
    
except socket.error as e:
    print(f"Socket error: {e}")
    exit()


while True:
    try:
        # Accepting incoming connection
        incomingSocket, incomingAddress = myTCPSocket.accept()
        print(f"Accepted connection from {incomingAddress}")

        # Loop for sending multiple messages to the client
        while True:
            # Receiving message from client
            myData = incomingSocket.recv(1024)
            if not myData:
                print("Client has disconnected.")
                break

            myData = myData.decode('utf-8')
            print(f"Received from client: {myData}")

            # Convert the message to uppercase
            myData = myData.upper()

            # Sending message back to the client
            incomingSocket.send(myData.encode('utf-8'))

        incomingSocket.close()

    except socket.error as e:
        print(f"Socket error: {e}")
        break

myTCPSocket.close()