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


                fridge_data = collection_virtual.find({
                    "payload.parent_asset_uid": "433-6a1-735-3ei", # actual fridge asset UID
                    "payload.timestamp": {
                        "$gte": int(three_hours_ago.timestamp() * 1000),
                        "$lte": int(current_pst.timestamp() * 1000)}
                }, {"_id": 0, "payload.Moisture Meter - Moisture Meter - Fridge": 1}) #only get sensor data

                moisture_readings = [
                    float(doc["payload"]["Moisture Meter - Moisture Meter - Fridge"]) for doc in fridge_data
                ]


                if moisture_readings:
                    avg_moisture = sum(moisture_readings) / len(moisture_readings)
                    avg_rh = (avg_moisture / 40) * 100
                    response = f"Average moisture (RH%) in the last 3 hours: {avg_rh:.2f}%"
                else:
                    response = "No data found for the last 3 hours."

                incomingSocket.send(response.encode('utf-8'))


            elif myData == "2": #avg water consumption per cycle for dishwasher
                dishwasher_data = collection_virtual.find({
                    "payload.parent_asset_uid": "ddo-08g-5f4-jsp"
                }, {"_id": 0, "payload.Water Consumption Sensor - Dishwasher": 1}) #only get sensor data

                water_readings = [
                    float(doc["payload"]["Water Consumption Sensor - Dishwasher"]) for doc in dishwasher_data
                ]

                if water_readings:
                    avg_cons = sum(water_readings)/len(water_readings)
                    response = f"Average Water Consumption (in gallons) per cycle: {avg_cons:.2f}"
                else:
                    response = "No data found for water consumption sensor."

                incomingSocket.send(response.encode('utf-8'))

            elif myData == "3": #which device consumed most electricity

                fridge_1 = collection_virtual.find({
                    "payload.Ammeter - Fridge": {"$exists":True}
                }) #only Ammeter sensor data

                dishwasher_data = collection_virtual.find({
                    "payload.Ammeter - Dishwasher": {"$exists":True}
                })  # only Ammeter sensor data

                fridge_2 = collection_virtual.find({
                    "payload.sensor 2 a087ce6e-4be6-4a0b-ba16-8ad7016af76a": {"$exists":True}
                }) #only Ammeter sensor data


                #store data for all devices
                fridge_1_readings = []  # collects only one sensor value per hour
                unique1_hours = []
                for doc in fridge_1:
                    time = doc["time"]
                    hour = datetime(time.year, time.month, time.day, time.hour)
                    if hour not in unique1_hours:
                        unique1_hours.append(hour)
                        fridge_1_readings.append(float(doc["payload"]["Ammeter - Fridge"]))


                dishwasher_readings = [
                    float(doc["payload"]["Ammeter - Dishwasher"]) for doc in dishwasher_data
                ]

                fridge_2_readings = []  # collects only one sensor value per hour
                unique2_hours = []
                for doc in fridge_2:
                    time = doc["time"]
                    hour = datetime(time.year, time.month, time.day, time.hour)
                    if hour not in unique2_hours:
                        unique2_hours.append(hour)
                        fridge_2_readings.append(float(doc["payload"]["sensor 2 a087ce6e-4be6-4a0b-ba16-8ad7016af76a"]))


                #CONVERSIONS : kWh = Amps x Volts x Hours / 1000

                #dishwasher: assuming 120 volts
                #dishwasher: assuming 1 cycle = 1 hour
                #dishwasher readings currently in Amperes
                if dishwasher_readings:
                    dish_avg_amps = sum(dishwasher_readings)/len(dishwasher_readings)
                else:
                    dish_avg_amps = 0
                dish_kWh = (dish_avg_amps * 120 * len(dishwasher_readings))/1000

                #fridge: assuming 120 volts
                #fridge: readings currently in Amperes

                #Smart Fridge 1
                if fridge_1_readings:
                    fr1_avg_amps = sum(fridge_1_readings) / len(fridge_1_readings)
                else:
                    fr1_avg_amps = 0
                fr1_kWh = (fr1_avg_amps * 120 * len(unique1_hours)) / 1000

                #Smart Fridge 2
                if fridge_2_readings:
                    fr2_avg_amps = sum(fridge_2_readings) / len(fridge_2_readings)
                else:
                    fr2_avg_amps = 0
                fr2_kWh = (fr2_avg_amps * 120 * len(unique2_hours))/1000

                max_kWh = max(dish_kWh, fr1_kWh, fr2_kWh)
                devices = []
                if fr1_kWh == max_kWh:
                    devices.append("Smart Fridge 1")
                if fr2_kWh == max_kWh:
                    devices.append("Smart Fridge 2")
                if dish_kWh == max_kWh:
                    devices.append("Smart Dishwasher")


                response = f"Max kWh consumed: {max_kWh} by following devices: {devices}"
                incomingSocket.send(response.encode('utf-8'))

            else:
                response = "Invalid query. Try again."
                incomingSocket.send(response.encode('utf-8'))


        incomingSocket.close()

    except socket.error as e:
        print(f"Socket error: {e}")
        break

myTCPSocket.close()

#VFVxIjUPSfYCoYPb