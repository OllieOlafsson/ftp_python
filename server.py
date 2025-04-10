#server
import socket

HOST = ''
PORT = 8999
print("- Server has started. -")

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        print(conn)
        with conn:
            with open('output', 'wb') as file:   
                while True:
                    data = conn.recv(4096)
                    file.write(data)
                    print(f"Received data {data}.")
                    if not data: break

