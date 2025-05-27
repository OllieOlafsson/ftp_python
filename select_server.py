import socket
import select
import io
import os

# I/O-related variables
path = './files/'
save_location = './server/'

# Socket 
timeout = 60
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('localhost', 8000)
server.setblocking(False)

option = b''

print (f'starting server on {server_address}')
server.bind(server_address)
server.listen(5)

formats = {
        # JPG -> 10 bytes header required
        "jpg": [
            b'\xff\xd8\xff\xe0\x00\x10JFIF', 
            b'\xff\xd8\xff\xe1\x14\x0cExif',
            ],
        # GIF -> 6 bytes header required
        "gif" : [b'GIF89a']
        }

# Lists
potential_readers = [ server ]
potential_writers = [] 
potential_errs = []
chunks = []

def transmit(sock, msg):
    count = 0
    totalsent = 0
    # Check if message to be sent is a file
    if isinstance(msg, io.BufferedReader):
        TOTALSIZE = f'{file_size:<10}'
        print(TOTALSIZE, "bytes to send")
    else: 
        TOTALSIZE = f'{len(msg):<10}'
        print (f'{len(msg):<10} bytes to send')

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
        return msg 

def receive(sock):
    count = 0
    bytes_received = 0
    # Receive tota size of message
    FULLSIZE_HEADER = sock.recv(10)
    print(FULLSIZE_HEADER, "bytes to receive") 
    if int(FULLSIZE_HEADER) > 4096:
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

def list_tree(sock):
    all_items = os.listdir(path)
    no_of_items = len(all_items)
    transmit(sock, str(no_of_items).encode('utf-8'))
    for i, j in enumerate(all_items):
        print(transmit(sock, str(j).encode('utf-8')))
    item_choice = receive(sock)
    print(item_choice)
    file_location = f'{path}{all_items[int(item_choice)]}'
    global file_size 
    file_size = os.path.getsize(file_location)
    with open(file_location, 'rb') as file:
       transmit(sock, file) 

while potential_readers:    
    print("Selecting from lists... ")
    ready_to_read, ready_to_write, in_error = \
            select.select( 
                          potential_readers, 
                          potential_writers, 
                          potential_errs,
                          timeout
                        )   
    print(potential_writers)

    for sock in ready_to_read:
        print("_goto 1")
        print(f"<fd{sock.fileno()}>")
        if sock is server:
            connection, client_address = sock.accept()
            print(f'new connection from {client_address}')
            connection.setblocking(True)
            potential_readers.append(connection)
        else:
            option = receive(sock)
            data = b''
            print(option)
            if option == b'1':
                data = receive(sock)
            if option:
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
        if (option == b'2'):
            list_tree(sock)

        if chunks:
            print(f'sending acknowledgement')
            transmit(sock, b'Data received')
            write_uploaded_file()
            potential_writers.remove(sock)
            potential_readers.remove(sock)
            del chunks[:]
        else: 
            print("No chunk")               
            sock.close()

    for sock in in_error:
        print(f'handling exception for {sock.getpeername()}')
        potential_readers.remove(s)
        if sock in potential_writers:
            potential_writers.remove(sock)
        sock.close()

