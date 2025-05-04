import socket
import threading
import os

HOST = ''
PORT = 8000
MSGLEN = 4096
path = '.'

def client_download(conn, addr):
    tree = bytearray()
    for item in os.listdir(path):
        tree = item.encode('utf-8') 
        print(transmit(conn, tree))
        print(tree)
    file_selection = receive(conn)
    index = int(file_selection.decode())
    print(index)

def client_upload(conn, addr):
    #Writing to 'output' file client is sending
    count = 0
    with open("output", 'wb') as file:
        while True:
            data = receive(conn)
            count += 1
            if not data:break
            file.write(data) 
            print (f"[{count}] Received {MSGLEN}")

def transmit(conn, msg):
    totalsent = 0
    while totalsent < MSGLEN:
        sent = conn.send(msg[totalsent:]) 
        if sent == 0:
            break
        totalsent = totalsent + sent

def receive(conn):
    chunks = []
    bytes_received = 0
    while bytes_received < MSGLEN:
        chunk = conn.recv(MSGLEN)
        if chunk == b'':
            break
        chunks.append(chunk)
        bytes_received = bytes_received + len(chunk)
        return b''.join(chunks)
        
def start():
    print("- Server has started -")
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen()
            conn, addr = server.accept()
            with conn:
                # Operation selection from client
                operation = receive(conn)
                print(f"Client has selected option {operation.decode('utf-8')}")
                if (operation == b'1'):
                    transmit(conn, b'Upload operation selected')
                    client_upload(conn, addr)
                    transmit(conn, b'Data was uploaded successfully')
                elif (operation == b'2'):
                    transmit(conn, b'Download operation selected')
                    client_download(conn, addr)

start()
