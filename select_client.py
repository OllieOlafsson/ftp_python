import socket
import select
import sys
import os
import io

# I/O 
file_location = './files/the-golden-one-the-glorious-lion.gif'
file_size = os.path.getsize(file_location)
save_location = './client/'
chunks = []

# Socket
timeout = 60
server_address = ('localhost', 8000)

formats = {
        # JPG -> 10 bytes header required
        "jpg": [
            b'\xff\xd8\xff\xe0\x00\x10JFIF', 
            b'\xff\xd8\xff\xe1\x14\x0cExif',
            ],
        # GIF -> 6 bytes header required
        "gif" : [b'GIF89a']
        }

def transmit(sock, msg):
    count = 0
    totalsent = 0
    # Check if message to be sent is a file
    if isinstance(msg, io.BufferedReader):
        TOTALSIZE = f'{file_size:<10}'
        print(TOTALSIZE, "bytes to send")
    else: 
        TOTALSIZE = f'{len(msg):<10}'
        print (f'{len(msg)} bytes to send')

    # Send total size of message
    sock.send(TOTALSIZE.encode('utf-8'))
    if int(TOTALSIZE) > 4096:
        while totalsent < int(TOTALSIZE):
            print(f'[{count}]{totalsent} sent')
            data = msg.read(4096)
            if data == b'': break
            #print(data[:10])
            SEGMENT_HEADER = f'{4096:<10}'
            # Send segment header
            sock.send(SEGMENT_HEADER.encode('utf-8'))
            # Send chunk
            sent = sock.send(data)
            count+=1
            totalsent += len(data)
        return totalsent
    else:
        sent = sock.send(msg)
        totalsent += len(msg)
        print(f"{msg} sent.")
        return msg

def receive(sock):
    count = 0
    bytes_received = 0
    # Receive tota size of message
    FULLSIZE_HEADER = sock.recv(10)
    print(FULLSIZE_HEADER, "bytes to receive") 
    if int (FULLSIZE_HEADER) > 4096:
        while bytes_received < int(FULLSIZE_HEADER):
            print(f'[{count}]{bytes_received} bytes received')
            # Receive segment header
            SEGMENT_HEADER = int(sock.recv(10))
            # Receive chunk of data
            chunk = sock.recv(SEGMENT_HEADER)
            chunks.append(chunk)
            if chunk == b'': break
            count += 1
            bytes_received += len(chunk)
        return bytes_received
    else:
        msg = sock.recv(int(FULLSIZE_HEADER))
        bytes_received += len(msg)
        return msg

def write_uploaded_file():
    chunks_joined = b''.join(chunks)
    for form, typ in formats.items():
        if form == "gif":
            for each in typ:
                print(each)
                if each == chunks_joined[:6]:
                    print(f"Identified format: {form}")
                    with open(f"{save_location}output.{form}", 'wb') as file:
                        file.write(chunks_joined)
        else:
            for each in typ:
                if each == chunks_joined[:10]:
                    print(f"Identified format: {form}")
                    with open(f"{save_location}output.{form}", 'wb') as file:
                        print(file.write(chunks_joined))

def server_tree(sock):
    received = 0
    all_items = []
    no_of_items = receive(sock)
    while received < int(no_of_items):
        item = receive(sock)
        all_items.append(item)  
        received += 1
    for i, j in enumerate(all_items):
        print(f"{i}. {j}")
    item_choice = input("Choose an item to download: ")
    print(item_choice)
    transmit(sock, item_choice.encode('utf-8'))


# TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setblocking(False)

print (f'connecting to {server_address} .')
sock.connect(server_address)

print("[1] Upload local file to server. ")
print("[2] Download file from server. ")
option = input("Enter your option: ").encode('utf-8')
print(transmit(sock, option))

if option == b'1':
    with open(file_location, 'rb') as file:
        transmit(sock, file)
    data = receive(sock)
    print("Received", data, "from", sock.getsockname())
    if not data:
        print("Closing socket", sock.getsockname())
        sock.close()
elif option == b'2':
    print(server_tree(sock))
    data = receive(sock)
    write_uploaded_file()
    sock.close()


