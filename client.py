#client
import socket
import sys
import os

IP = '192.168.1.137'
PORT = 8000
MSGLEN = 4096
file_location = './flag.gif'
count = 0

def receive(s):
    chunks = []
    bytes_received = 0
    while bytes_received < MSGLEN:
        chunk = s.recv(MSGLEN)
        if chunk == b'':
            break
        chunks.append(chunk)
        bytes_received = bytes_received + len(chunk)
        return b''.join(chunks)

def transmit(s, msg):
    totalsent = 0
    while totalsent < MSGLEN:
        sent = s.send(msg[totalsent:]) 
        if sent == 0:
            break
        totalsent = totalsent + sent


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((IP, PORT))
    s.settimeout(5)

    operation = input("Options: \n1. Upload a file to server\n2. Download a file from server\n>>").encode('utf-8')
    SYN = transmit(s, operation)      #send option to socket
    # Upload
    if (operation == b'1'):     
        with open(file_location, 'rb') as file:
            ACK = receive(s)        #Receive acknowledgement of selection
            print(ACK)

            file_size = os.path.getsize(file_location)
            print(file_size)
            data = file.read(file_size)
         
            PAYLOAD = transmit(s, data)       #send data
            SYN_ACK = receive(s)    # ack wether data was uploaded successfully
            print(type(SYN_ACK))


    # Download
    elif (operation == b'2'):
        ACK = receive(s)      # Receive acknowledgement message
        print(ACK)

        count += 1
        TREE_OUTPUT = receive(s)
        #print(f"{count}. {reply.decode()}")
        selection = input("Select file (by number): ").encode('utf-8')
        transmit(selection)


