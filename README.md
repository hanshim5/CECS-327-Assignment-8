# CECS-327-Assignment-8
Instructions for Users

To run programs:
1. Open the terminal for running server code.
    Run the server code: python "Echo Server - Modified.py".
2. Open terminal for running client code.
    Run the client code: python "Echo Client- Modified.py".
3. Input the IP address and port number. To connect to a local machine, use the IP address [#].
4. After confirming connection to the server, input a query number to send.
5. The server should reply with results corresponding to the query number.
6. Type 'exit' to quit or input another message.

To make server port open only to local machine:
1. Use myTCPSocket.bind((localhost, 1024)) in "Echo Server - Modified.py" code.

To make server port open to the outside world:
1. Use myTCPSocket.bind(('0.0.0.0', 1024)) instead of localhost in "Echo Server - Modified.py" code.