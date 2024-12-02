# cd C:\Users\hanna\CECS 327
# python "Echo Server.py"

# Isela's local IP: 
# 172.20.10.2
# 1026

from pymongo import MongoClient
import socket
import certifi
import getpass
from datetime import datetime, timedelta
import pytz

#Mongo connection
try:
    password = getpass.getpass("Mongo db password: ")
    cluster = f"mongodb+srv://iselat5862:{password}@cluster0.goumq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(cluster, tlsCAFile=certifi.where())
    db = client['test']
    collection_metadata = db['IoT Devices_metadata']
    collection_virtual = db['IoT Devices_virtual']

    print("Mongo Collection names:")
    print(db.list_collection_names())
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# PST timezone
def get_pst():
    utc_now = datetime.now(pytz.utc)
    pst = pytz.timezone("America/Los_Angeles")
    return utc_now.astimezone(pst)


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
            myData = incomingSocket.recv(1024).decode('utf-8')
            if not myData:
                print("Client has disconnected.")
                break

            if myData == '1': # Avg fridge moisture in past 3 hours
                current_pst = get_pst()
                three_hours_ago = current_pst - timedelta(hours=3)

                # Query the database
                fridge_data = collection_virtual.find({
                    "asset_uid": "433-6a1-735-3ei",  # actual fridge asset UID
                    "payload.timestamp": {
                        "$gte": int(three_hours_ago.timestamp() * 1000),
                        "$lte": int(current_pst.timestamp() * 1000)
                    }
                })
                moisture_readings = [
                    float(doc["payload"]["Moisture Meter - Moisture Meter"]) for doc in fridge_data
                ]
                if moisture_readings:
                    avg_moisture = sum(moisture_readings) / len(moisture_readings)
                    avg_rh = (avg_moisture / 40) * 100
                    response = f"Average moisture (RH%) in the last 3 hours: {avg_rh:.2f}%"
                else:
                    response = "No data found for the last 3 hours."
                incomingSocket.send(response.encode('utf-8'))
            else:
                response = "Invalid query. Try again."
                incomingSocket.send(response.encode('utf-8'))

        incomingSocket.close()

    except socket.error as e:
        print(f"Socket error: {e}")
        break

myTCPSocket.close()

#VFVxljUPSfYCoYPb