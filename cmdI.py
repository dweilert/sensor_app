import socket 
import sys 
 
SERVER_PATH = "/tmp/sensor_server_socket" 
 
def run_unix_domain_socket_client(): 
    """ Run "a Unix domain socket client """ 
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) 
     
    # Connect the socket to the path where the server is listening 
    server_address = SERVER_PATH  
    print ("connecting to %s" % server_address) 
    try: 
        sock.connect(server_address) 
    except socket.error as msg: 
        print (msg) 
        sys.exit(1) 
     
    try: 
        while True:
            message = input("Enter command: ")
            #message = "This is the message.  This will be echoed back!"
            if message == "quit" or message = "bye" or message == "q"
                break 
            print  ("Sending [%s]" %message) 
    
            sock.sendall(bytes(message, 'utf-8')) 
            # Comment out the above line and uncomment the below line for Python 2.7. 
            # sock.sendall(message) 
    
            amount_received = 0 
            amount_expected = len(message) 
            
            while amount_received < amount_expected: 
                data = sock.recv(16) 
                amount_received += len(data) 
                print ("Received [%s]" % data) 
     
    finally: 
        print ("Finished") 
        sock.close() 
 
if __name__ == '__main__': 
    run_unix_domain_socket_client() 