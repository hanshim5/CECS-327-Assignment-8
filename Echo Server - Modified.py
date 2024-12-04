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

# Mongo connection setup
try:
    password = getpass.getpass("Mongo db password: ")
    cluster = f"mongodb+srv://iselat5862:{password}@cluster0.goumq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    # Create MongoDB client with certificate authentication
    client = MongoClient(cluster, tlsCAFile=certifi.where())
    db = client['test']

    # Collections within database
    collection_metadata = db['IoT Devices_metadata']
    collection_virtual = db['IoT Devices_virtual']

    # Print available collections
    print("Mongo Collection names:")
    print(db.list_collection_names())
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# Get current time in PST timezone
def get_pst():
    utc_now = datetime.now(pytz.utc)
    pst = pytz.timezone("America/Los_Angeles")
    return utc_now.astimezone(pst)


# BST Data Structure
class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        # Insert value into BST
        if self.root is None:
            self.root = BSTNode(value) # Create root if tree empty
        else:
            self.insert_recursive(self.root, value)

    def insert_recursive(self, node, value):
        # Insertion logic
        if value < node.value:
            if node.left is None:
                node.left = BSTNode(value)
            else:
                self.insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = BSTNode(value)
            else:
                self.insert_recursive(node.right, value)

    def find_max(self):
        # Find the maximum value in the BST
        return self._find_max(self.root)

    def _find_max(self, node):
        if node.right is None:
            return node.value  # Maximum value is the rightmost node
        return self._find_max(node.right)

    def find_min(self):
        # Find the minimum value in the BST
        return self._find_min(self.root)

    def _find_min(self, node):
        if node.left is None:
            return node.value  # Minimum value is the leftmost node
        return self._find_min(node.left)

    def calculate_average(self):
        # Calculate the average value of all nodes in the BST
        total, count = self.calculate_sum_and_count(self.root)
        return total / count if count > 0 else 0

    def calculate_sum_and_count(self, node): 
        # Helper function to calculate the sum and count of nodes
        if node is None:
            return 0, 0
        left_sum, left_count = self.calculate_sum_and_count(node.left)
        right_sum, right_count = self.calculate_sum_and_count(node.right)
        return left_sum + right_sum + node.value, left_count + right_count + 1



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
                }, {"_id": 0, "payload.Moisture Meter - Fridge": 1}) # only get sensor data
                
                print("Fridge Data:", list(fridge_data))  # Convert cursor to list for debugging

                moisture_readings = BST() # Store readings in a BST and calculate the average
                for doc in fridge_data:
                    moisture_readings.insert(float(doc["payload"]["Moisture Meter - Fridge"]))

                avg_moisture = moisture_readings.calculate_average()
                if avg_moisture == 0:
                    response = "\nNo data generated in past 3 hours.\n"
                else:
                    avg_rh = (avg_moisture / 40) * 100
                    response = f"\nAverage moisture (RH%) in the last 3 hours: {avg_rh:.2f}%\n"
                incomingSocket.send(response.encode('utf-8'))


            elif myData == "2": # avg water consumption per cycle for dishwasher
                dishwasher_data = collection_virtual.find({
                    "payload.parent_asset_uid": "ddo-08g-5f4-jsp"
                }, {"_id": 0, "payload.Water Consumption Sensor - Dishwasher": 1}) # only get sensor data

                water_readings = BST()
                for doc in dishwasher_data:
                    water_readings.insert(float(doc["payload"]["Water Consumption Sensor - Dishwasher"]))


                avg_cons = water_readings.calculate_average()
                if avg_cons == 0:
                    response = "\nNo data found for water consumption sensor.\n"
                else:
                    response = f"\nAverage Water Consumption (in gallons) per cycle: {avg_cons:.2f}\n"
                incomingSocket.send(response.encode('utf-8'))

            elif myData == "3": # which device consumed most electricity

                fridge_1 = collection_virtual.find({
                    "payload.Ammeter - Fridge": {"$exists":True}
                }) # only Ammeter sensor data

                dishwasher_data = collection_virtual.find({
                    "payload.Ammeter - Dishwasher": {"$exists":True}
                })  # only Ammeter sensor data

                fridge_2 = collection_virtual.find({
                    "payload.sensor 2 a087ce6e-4be6-4a0b-ba16-8ad7016af76a": {"$exists":True}
                }) # only Ammeter sensor data


                # store data for all devices
                fridge_1_readings = BST() # holds one sensor value per hour
                unique1_hours = []
                for doc in fridge_1:
                    time = doc["time"]
                    hour = datetime(time.year, time.month, time.day, time.hour)
                    if hour not in unique1_hours:
                        unique1_hours.append(hour)
                        # adds only one sensor value per hour
                        fridge_1_readings.insert(float(doc["payload"]["Ammeter - Fridge"]))


                dishwasher_readings = BST()
                dish_hours = 0
                for doc in dishwasher_data:
                    dishwasher_readings.insert(float(doc["payload"]["Ammeter - Dishwasher"]))
                    dish_hours += 1   # assuming each data entry counts as 1 hour

                fridge_2_readings = BST() # holds one sensor value per hour
                unique2_hours = []
                for doc in fridge_2:
                    time = doc["time"]
                    hour = datetime(time.year, time.month, time.day, time.hour)
                    if hour not in unique2_hours:
                        unique2_hours.append(hour)
                        # adds only one sensor value per hour
                        fridge_2_readings.insert(float(doc["payload"]["sensor 2 a087ce6e-4be6-4a0b-ba16-8ad7016af76a"]))


                # CONVERSIONS : kWh = Amps x Volts x Hours / 1000

                # dishwasher: assuming 120 volts
                # dishwasher: assuming 1 cycle = 1 hour
                # dishwasher readings currently in Amperes
                dish_avg_amps = dishwasher_readings.calculate_average()
                dish_kWh = (dish_avg_amps * 120 * dish_hours)/1000

                # fridge: assuming 120 volts
                # fridge: readings currently in Amperes
                # Smart Fridge 1
                fr1_avg_amps = fridge_1_readings.calculate_average()
                fr1_kWh = (fr1_avg_amps * 120 * len(unique1_hours)) / 1000

                # Smart Fridge 2
                fr2_avg_amps = fridge_2_readings.calculate_average()
                fr2_kWh = (fr2_avg_amps * 120 * len(unique2_hours))/1000

                max_kWh = max(dish_kWh, fr1_kWh, fr2_kWh)
                devices = []
                if fr1_kWh == max_kWh:
                    devices.append("Smart Fridge 1")
                if fr2_kWh == max_kWh:
                    devices.append("Smart Fridge 2")
                if dish_kWh == max_kWh:
                    devices.append("Smart Dishwasher")


                response = f"\nMax kWh consumed: {max_kWh:.2f} by following devices: {devices}\n"
                incomingSocket.send(response.encode('utf-8'))

            else:
                #Invalid query
                response = "\nInvalid query. Try again.\n"
                incomingSocket.send(response.encode('utf-8'))

        #Close client connection
        incomingSocket.close()

    except socket.error as e:
        print(f"Socket error: {e}")
        break

#Close server socket
myTCPSocket.close()

#VFVxIjUPSfYCoYPb
#python "Echo Server - Modified.py"