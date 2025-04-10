import socket
import threading

HOST = ''
PORT = 8999
data_size = 4096

#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.bind((HOST, PORT)) 

def client_connection(conn, addr):
    with conn:
        thread = threading.Thread(target = client_upload, args=(conn, addr))
        thread.start()
        print(f"Active threads: {threading.enumerate()}")
        thread.join()

def client_upload(conn, addr):
    count = 0
    with open("output", 'wb') as file:
        while True:
            count += 1
            data = conn.recv(data_size)
            file.write(data)
            print(f"[{count}] Received data {data_size}")
            if not data: break
        
def start():
    print("- Server has started -")
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((HOST, PORT))
            server.listen()
            conn, addr = server.accept()
            client_connection(conn, addr)

start()
