import socket 
import sys 
 
SERVER_PATH = "/tmp/sensor_server_socket" 
 
def run_unix_domain_socket_client(): 
    """ Run "a Unix domain socket client """ 
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) 
     
    # Connect the socket to the path where the server is listening 
    server_address = SERVER_PATH  
    print (f"Connecting to senor command interface at {server_address}") 
    try: 
        sock.connect(server_address) 
    except socket.error as msg: 
        print (msg) 
        sys.exit(1) 
     
    try: 
        while True:
            message = input("Enter command: ")
            #message = "This is the message.  This will be echoed back!"
            if message == "quit" or message == "bye" or message == "q":
                break 
            sock.sendall(bytes(message, 'utf-8')) 
            data = sock.recv(1024)
            print(f"Received: {data}")
     
    finally: 
        print ("Finished") 
        sock.close() 
 
if __name__ == '__main__': 
    run_unix_domain_socket_client() 