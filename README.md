# CECS-327-Assignment-8
Instructions for Users

Note: Make sure to have pymongo, pytz, and certifi libraries installed. Additionally, the getpass library(used to securely handle passwords) may/may not work in certain environments. If it doesn't work on your device, hardcode the password into the connection string instead.

To run programs:
1. Open the terminal in one of the VMs for running server code.
    Run the server code: python "Echo Server - Modified.py".
2. Open terminal in the other VM for running client code.
    Run the client code: python "Echo Client- Modified.py".
3. For the VM running the server, input its own internal IP address and port number.
4. For the terminal running the client, input the other VM's external IP address and port number.
    - After confirming connection to the server, input a query number to send.
6. The server should reply with data corresponding to the query number.
7. Type 'exit' to quit or input another message.

To make server port open only to local machine:
1. Use myTCPSocket.bind((localhost, 1024)) in "Echo Server - Modified.py" code.

To make server port open to the outside world:
1. Use myTCPSocket.bind(('0.0.0.0', 1024)) instead of localhost in "Echo Server - Modified.py" code.

**Link to Presentation**
https://docs.google.com/presentation/d/1RXiattxdW9Ff_BaePf_Tz_LJcpDSEGQ-UqSVMeQVWKw/edit?usp=sharing

**Link to Report**
https://docs.google.com/document/d/12T0-dqpHloUMm-S3Yp0ANH2jb-4fhk6vDVpRqX6JSYg/edit?usp=sharing
