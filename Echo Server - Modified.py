# cd C:\Users\hanna\CECS 327
# python "Echo Server.py"

# Isela's local IP: 
# 172.20.10.2
# 1026

# 1. Receives the message from the client.
# 2. Change the letters of the message to "capital letters" and send it back to the client by using the same socket.
# 3. The server should be able to send multiple messages to the client. You may need to consider using the infinite loop as we discussed in the class.

import socket

# Creating a TCP socket
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binding socket to IP address and port number
myTCPSocket.bind(('0.0.0.0', 1024))#('localhost', 1024))

# Listening for incoming client connections
myTCPSocket.listen(5)
print("Server is listening on port 1024...")

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
