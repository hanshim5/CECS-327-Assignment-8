
'''
1. Prompts the user to input the IP address, port number of the server, and a message to send to that server.
2. Sends the message to the server.
3. Display the server replay by using the same socket.
4. Displays an error message if the IP address or port number were entered incorrectly.
5. The client should be able to send multiple messages to the server. You may need to consider using the infinite loop as we discussed in the class.
'''
import socket

# Define buffer size
maxBytesToReceive = 1024

# Define valid queries
valid_queries = [
    "1. What is the average moisture inside my kitchen fridge in the past three hours?",
    "2. What is the average water consumption per cycle in my smart dishwasher?",
    "3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]


def display_queries():
    for query in valid_queries:
        print(f"  - {query}")

while True:
    try:
        # Prompt the user to input the IP address
        ip_address = input("Please input the IP address (or 'exit' to quit): ")
        if ip_address.lower() == 'exit':
            print("Exiting client.")
            break

        # Prompt the user to input the port number
        port_number_input = input("Please input the server's port number: ")
        
        # Convert port number input to an integer
        try:
            port_number = int(port_number_input)
        except ValueError:
            print("Error: Please enter a valid port number (an integer).")
            continue

        # Create a TCP socket
        myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Try to connect to the server
        myTCPSocket.connect((str(ip_address), port_number))
        print("Connected to the server.")
        
        # Send multiple messages to the server
        while True:
            display_queries()
            message = input("Please input a query number to send to the server (or type 'exit' to quit): ")
            
            if message.lower() == 'exit':
                print("Exiting...")
                break
            
            if message in ['1', '2', '3']:
                # Send the message to the server
                myTCPSocket.send(message.encode('utf-8'))
                
                # Receive and display the server's response
                serverResponse = myTCPSocket.recv(maxBytesToReceive)
                print("Server's reply:", serverResponse.decode('utf-8'))
            else:
                print("Sorry, this query cannot be processed. Please try one of the following:")
                display_queries()

        myTCPSocket.close()
        break

    except socket.error as e:
        print(f"Error: Unable to connect or communicate with the server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
