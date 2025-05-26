import socket
import select

timeout = 60
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('localhost', 8000)
server.setblocking(False)

print (f'starting server on {server_address}')
server.bind(server_address)
server.listen(5)

formats = {
        "jpg" : b'\xff\xd8\xff\xe0\x00\x10JFIF',
        "gif" : b'GIF89a\xe0\x01\xe0\x01'
        }

potential_readers = [ server ]
potential_writers = [] 
potential_errs = []
chunks = []

def receive(sock):
    count = 0
    bytes_received = 0
    while True:
        # Receive tota size of message
        FULLSIZE_HEADER = sock.recv(10)
        print(FULLSIZE_HEADER, "bytes to receive") 
        while bytes_received < int(FULLSIZE_HEADER):
            print(f'[{count}]{bytes_received} bytes received')
            # Receive segment header
            SEGMENT_HEADER = int(sock.recv(4))
            # Receive chunk of data
            chunk = sock.recv(SEGMENT_HEADER)
            chunks.append(chunk)
            if chunk == b'': break
            count += 1
            bytes_received += len(chunk)
        for form in formats:
            for chunk in chunks:
                if (chunk[:10] == formats[form]):
                    print("Identified format", form)
                    found_format = form
                    break
                else:
                    print("Unidentified format", form)
                    break
    for chunk in chunks:
        with open(f"loutput.{found_format}", 'wb') as file:
                    file.write(chunk)
    return bytes_received

while potential_readers:    
    print("Selecting from lists... ")
    ready_to_read, ready_to_write, in_error = \
            select.select( 
                          potential_readers, 
                          potential_writers, 
                          potential_errs,
                          timeout
                        )   
    print(ready_to_read)

    for sock in ready_to_read:
        print("_goto 1")
        print(f"<fd{sock.fileno()}>")
        if sock is server:
            connection, client_address = sock.accept()
            print(f'new connection from {client_address}')
            connection.setblocking(False)
            potential_readers.append(connection)
        else:
            data = receive(sock)
            if data:
                print(f'received {data} from {sock}')
                if sock not in potential_writers:
                    potential_writers.append(sock)
            else:
                print(f'closing {client_address}')
                if sock in potential_writers:
                    potential_writers.remove(sock)
                    sock.close()

    for sock in ready_to_write:
        print("_goto 2")
        print(f"<fd{sock.fileno()}>")
#        for datum in chunks:
#            with open("output", 'wb') as file:
#                file.write(datum)
        if chunks:
            print(f'sending acknowledgement')
            sock.send(b'Data received')
            potential_writers.remove(sock)
            potential_readers.remove(sock)
            del chunks[:]
        else: 
            print("No chunk")               
            sock.shutdown(socket.SHUT_WR)

    for sock in in_error:
        print(f'handling exception for {sock.getpeername()}')
        potential_readers.remove(s)
        if sock in potential_writers:
            potential_writers.remove(sock)
        sock.close()

