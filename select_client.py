import socket
import select
import sys
import os
import io

timeout = 60
file_location = './ftp_python/hiromi.jpg'
file_size = os.path.getsize(file_location)

server_address = ('localhost', 8000)

def transmit(sock, msg):
    count = 0
    totalsent = 0
    # Check if message to be sent is a file
    if isinstance(msg, io.BufferedReader):
        TOTALSIZE = f'{file_size:<10}'
        print(TOTALSIZE, "bytes to send")
    else: 
        TOTALSIZE = len(msg)
        print (f'{len(msg)} bytes to send')

    # Send total size of message
    sock.send(TOTALSIZE.encode('utf-8'))
    if int(TOTALSIZE) > 4096:
        while totalsent < int(TOTALSIZE):
            #print(f'[{count}]{totalsent} sent')
            data = file.read(4096)
            #print(data[:10])
            SEGMENT_HEADER = f'{4096:<10}'
            # Send segment header
            sock.send(SEGMENT_HEADER.encode('utf-8'))
            # Send chunk
            sent = sock.send(data)
            if data == b'': break
            count+=1
            totalsent += len(data)
    else:
        sent = sock.send(msg[totalsent:])
        totalsent += len(msg)
        print(sent)
    return totalsent

# TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setblocking(False)

potential_readers = []
potential_writers = [ sock ]
potential_errs = []

ready_to_read, ready_to_write, in_error = \
        select.select(
                potential_readers,
                potential_writers,
                potential_errs,
                timeout
                )

print (f'connecting to {server_address} .')
sock.connect(server_address)

with open(file_location, 'rb') as file:
    transmit(sock, file)

data = sock.recv(1024)
print("Received", data, "from", sock.getsockname())
if not data:
    print("Closing socket", sock.getsockname())
    sock.close()
