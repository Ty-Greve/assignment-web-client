#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        o = urllib.parse.urlparse(url)
        host = o.hostname
        # print(host)
        port = o.port
        # print(port)
        # print(o.scheme)

        if (port == None and o.scheme == "https"):
            port = 443
        elif (port == None and o.scheme == "http"):
            port = 80
        else:
            # Check if an error message should be send in this case 
            pass
        # print(port)

        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # print("dada here")
        # print(data)
        # a = data.split("\n")[0].split(" ")
        # print("a here")
        # print(a)
        code = int((data.split("\r\n")[0]).split(" ")[1])
        # print(code)
        return code

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        # print(body)
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port = self.get_host_port(url)
        self.connect(host, port)

        self.sendall("GET " + url + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n")

        arrival = self.recvall(self.socket)
        # print(arrival)
        code = self.get_code(arrival)
        body = self.get_body(arrival)
        headers = self.get_headers(arrival)
        print(headers + "\r\n\r\n" + body)

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port = self.get_host_port(url)
        self.connect(host, port)

        if (args == None):
            self.sendall("POST " + url + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\nContent-Length: " + str(0) + "\r\n\r\n")
        else:
            contentLength = len(str(urllib.parse.urlencode(args)))
            self.sendall("POST " + url + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\nContent-Length: " + str(contentLength) + "\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n" + str(urllib.parse.urlencode(args)))

        arrival = self.recvall(self.socket)
        # print(arrival)
        code = self.get_code(arrival)
        body = self.get_body(arrival)
        headers = self.get_headers(arrival)
        print(headers + "\r\n\r\n" + body)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
