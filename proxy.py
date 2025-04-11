import os
import sys
from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

originServerPort = 8080
originServerName = sys.argv[1]


def handleResponse(connectionSocket, addr):

    requestHTTP = getrequest(connectionSocket)
    request = requestHTTP.split("\r\n")
    requestLine = request[0].split(" ")
    headers = {}
    for header in request[1:]:
        if ": " in header:
            key, value = header.split(": ", 1)
            headers[key] = value
    if "Host" not in headers:
        response = "HTTP/1.1 400 Bad Request\r\nVia: Proxy_Server\r\n\r\n"
    elif "GET" == requestLine[0]:
        filePath = requestLine[1].lstrip("/")

        try:
            lastModifiedTimestamp = os.path.getmtime(filePath)
            modifiedTime = datetime.utcfromtimestamp(lastModifiedTimestamp)
            formattedModifiedTime = modifiedTime.strftime("%a, %d %b %Y %H:%M:%S GMT")

            if "If-Modified-Since" in headers:
                clientTimeString = headers["If-Modified-Since"]
                headers["If-Modified-Since"] = formattedModifiedTime
                newRequest = changeOtherRequests(request[0], headers)
                responseOrigin = requestOrigin(newRequest)

                if "304 Not Modified" in responseOrigin:
                    try:
                        client_time = datetime.strptime(
                            clientTimeString, "%a, %d %b %Y %H:%M:%S GMT"
                        )
                        if client_time >= modifiedTime:
                            response = responseOrigin
                        else:
                            file = open(filePath, "r")
                            file_content = file.read()
                            contentLength = len(file_content)
                            response = (
                                f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {contentLength}\r\nVia: Proxy_Server\r\nLast-Modified: {formattedModifiedTime}\r\n\r\n"
                                + file_content
                            )
                    except ValueError:
                        response = (
                            "HTTP/1.1 400 Bad request\r\nVia: Proxy_Server\r\n\r\n"
                        )
                else:
                    response = responseOrigin

            else:
                headers["If-Modified-Since"] = formattedModifiedTime
                newRequest = changeOtherRequests(request[0], headers)
                responseOrigin = requestOrigin(newRequest)
                if "304 Not Modified" in responseOrigin:
                    file = open(filePath, "r")
                    file_content = file.read()
                    contentLength = len(file_content)
                    response = (
                        f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {contentLength}\r\nVia: Proxy_Server\r\nLast-Modified: {formattedModifiedTime}\r\n\r\n"
                        + file_content
                    )
                else:
                    response = responseOrigin
        except FileNotFoundError:
            newRequest = changeOtherRequests(request[0], headers)
            response = requestOrigin(newRequest)
    else:
        if ("Cache-Control" in requestHTTP) and (
            "no-store" in headers["Cache-Control"]
        ):
            newRequest = changeOtherRequests(request[0], headers)
            response = requestOrigin(newRequest)
        else:
            response = "HTTP/1.1 501 Not Implemented\r\nVia: Proxy_Server\r\n\r\n"

    connectionSocket.sendall(response.encode())
    connectionSocket.close()


def requestOrigin(request):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((originServerName, originServerPort))
    clientSocket.sendall(request.encode())
    fullResponse = []
    while True:
        responseSection = clientSocket.recv(1024).decode()
        if not responseSection:
            break
        fullResponse.append(responseSection)
    responseOrigin = "".join(fullResponse)
    return responseOrigin


def changeOtherRequests(requestline, headers):
    headers["Host"] = originServerName + ": " + str(originServerPort)
    headersCombined = "\r\n".join([f"{key}: {value}" for key, value in headers.items()])
    full_request = f"{requestline}\r\n{headersCombined}\r\n\r\n"
    return full_request


def getrequest(connectionSocket):
    full_message = []
    while True:
        requestSection = connectionSocket.recv(1024).decode()
        full_message.append(requestSection)

        if "\r\n\r\n" in requestSection:
            break
        if "\r\n" == requestSection:
            break
    request = "".join(full_message)
    return request


if __name__ == "__main__":

    serverPort = 80
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)

    while True:
        connectionSocket, addr = serverSocket.accept()
        client_thread = Thread(target=handleResponse, args=(connectionSocket, addr))
        client_thread.start()
