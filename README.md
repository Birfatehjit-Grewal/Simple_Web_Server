# Simple_Web_Server
This project includes 2 servers created using socket programming. The servers implemented basic HTTP Methods and messages. The servers can produce the following codes 200 OK, 304 Not Modified, 400 Bad Request, 404 Not Found, and 501 Not Implemented. The response is based on the RFC7231. The proxy server reduces the workload of the main server by caching the response for get requests by requesting the document from the main server as a conditional get request based on the cached file already in the proxy server.

## How to run the code
Use the latest version of python which can be downloaded from [here](https://www.python.org/downloads/)

Run the start_server.py first by running the following `python start_server.py` in the terminal or command prompt

Then Run the sender.py by running the following `python proxy.py <server_ip>` in the terminal or command prompt after filling out the needed paramaters.

* replace <server_ip> with the ip address of the computer running the start_server.py

The server is listening on port `8080` by default.

The proxy server is listening on port `80` by default.
