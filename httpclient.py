#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2022 Nasif Hossain
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
from urllib.parse import urlparse
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def generate_url_info(self, url):
        """
        " method to parse the url and get info out of it
        " returns the path, port and host
        """
        self.parsed_url = urlparse(url)        
        self.host_name = self.parsed_url.hostname
        self.url_path = self.parsed_url.path if self.parsed_url.path != "" else "/"
        self.url_port = self.parsed_url.port if self.parsed_url.port else 80

    def generate_request(self, command,  args = None):
        """
        "  function to return request from given url inputs
        """
        # # in either case if there are args
        if args != None:
            content = urllib.parse.urlencode(args)
        else:
            content = ""

        header = [f'{command} {self.url_path} HTTP/1.1\r\n',
                f'Host: {self.host_name}\r\n',
                "Connection: close\r\n",
                "User-Agent: nasif/1.0.1\r\n",
                "Content-Type: application/x-www-form-urlencoded\r\n",  
                f"Content-Length: {len(content)}\r\n\r\n"]

        # self.get_req_type(command, content)
        if command == "GET":
            return "".join(header)
        
        # POST
        elif command == "POST":
            header.append(f"{content}\r\n\r\n")
            return "".join(header)

        
    def generate_Header(self, data):
        header = data.split("\r\n\r\n")[0]
        return header[0], header[1]

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        parse_data = data.split("\r\n\r\n")
        code = int(parse_data[0].split('\r\n')[0].split()[1])
        return code

    def get_headers(self,data):
        parsed_data = data.split("\r\n\r\n")
        headers = parsed_data[0]
        return headers

    def get_body(self, data):
        parsed_data = data.split("\r\n\r\n")
        body = parsed_data[1]
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

        # parse and generate info from url input
        self.generate_url_info(url) 

        # connect to url to through socket connection
        self.connect(self.host_name, self.url_port)

        response_data = self.generate_request( "GET", args)
       
        self.sendall(response_data)
        data = self.recvall(self.socket)
        self.close()

        # stdout       
        code = self.get_code(data)
        body = self.get_body(data)

        print("Response code for GET:", code)
        print("Response body:", body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # parse and generate info from url input
        self.generate_url_info(url) 
        
        # connect to url to through socket connection
        self.connect(self.host_name, self.url_port)

        response_data = self.generate_request( "POST", args)
        self.sendall(response_data)
        data = self.recvall(self.socket)
        self.close()

        # stdout       
        code = self.get_code(data)
        body = self.get_body(data)

        print("Response code for POST:", code)
        print("Response body:", body)
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
