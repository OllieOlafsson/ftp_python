#client
import socket
import sys
import os

IP = '172.20.10.6'
PORT = 8999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    with open("/home/franco/Documents/Coding/Python/File Transfer server/ls", 'rb') as file:
        file_size = os.path.getsize("/home/franco/Documents/Coding/Python/File Transfer server/ls")
        print(file_size)
        data = file.read(file_size)

        s.connect((IP, PORT))
        s.sendall(data)
        #print(data)
        print(sys.getsizeof(data))
