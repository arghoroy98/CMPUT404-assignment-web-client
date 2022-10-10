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
        hostname = urllib.parse.urlparse(url).hostname
        port = urllib.parse.urlparse(url).port
        if not port:
            port = 80
        return hostname,port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(3)
        return None

    def get_code(self, data):
        return int(data.split(" ")[1])

    def get_headers(self,data):
        headers = data.split('\r\n\r\n')
        return headers[0]

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
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
            try:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
            except:
                break
        return buffer.decode(encoding='utf-8', errors="backslashreplace") #https://stackoverflow.com/questions/71395155/unicodedecodeerror-when-try-to-read-data-from-google-com-in-python
 

    def GET(self, url, args=None):
        (hostname, port) = self.get_host_port(url)
        # Now we will get the path if it exists
        target = urllib.parse.urlparse(url).path
        if not target:
            target = '/'    #If there is no path just use a /

        #Now let's prepare the headers to send
        headers = "GET {target} HTTP/1.1\r\nHost: {host}\r\n\r\n".format(target=target,host=hostname)
        try:
            self.connect(hostname,port)
            self.sendall(headers)
            data = self.recvall(self.socket)

            #This gets the response body, response header and response status code
            self.body = self.get_body(data)
            self.headers = self.get_headers(data)
            self.code = self.get_code(self.headers)
            self.close()
        except:
            self.close()
            self.code = 404
            return HTTPResponse(self.code, "")
        return HTTPResponse(self.code, self.body)


    def POST(self, url, args=None):
        (hostname, port) = self.get_host_port(url)
        # Now we will get the path if it exists
        target = urllib.parse.urlparse(url).path
        if not target:
            target = '/'    #If there is no path just use a /

        if args:
            data_to_send = urllib.parse.urlencode(args)
        else:
            data_to_send = ""

        data_length = len(data_to_send)

        #Now let's prepare the headers to send
        headers = "POST {target} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded  \r\nContent-length: {length} \r\n\r\n{data}".format(target=target,host=hostname, length=data_length, data=data_to_send)
        try:
            self.connect(hostname,port)
            self.sendall(headers)
            data = self.recvall(self.socket)
            #This gets the response body, response header and response status code
            self.body = self.get_body(data)
            self.headers = self.get_headers(data)
            self.code = self.get_code(self.headers)
            self.close()
        except:
            self.close()
            self.code = 404
            return HTTPResponse(self.code, "")
        return HTTPResponse(self.code, self.body)

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
