import socket
import pickle
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

SECRET_KEY = os.getenv("SECRET_KEY").encode()
f = Fernet(SECRET_KEY)

# in the function i secured the DB_HOST, DB_PORT in a .env so it is harder for outside elements to access it
def send_sql(query, params, DB_HOST=DB_HOST, DB_PORT=DB_PORT):
    print("send_sql requested")
    # socket.socket() creates a socket
    #                 AF_INET= ipv4    SOCK.STREAM = tcp      
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DB_HOST, DB_PORT))
        # pickle just turns the data into binary for tranmission
        payload = pickle.dumps((query, params))
        token = f.encrypt(payload)
        print(f"payload is sending: {payload[:100]}...")
        s.sendall(token)
        s.shutdown(socket.SHUT_WR)


        data = b""
        # it takes all of the data until it gets the end of message
        while True:
            #accepts the data in chunks 0f 4096b
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk

        plaintext = f.decrypt(data)
        # I chose to return it unorginized- return data
        # because diffrent functions will have diffrent types of data sent back
    return plaintext
