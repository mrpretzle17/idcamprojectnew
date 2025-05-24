import socket
import threading
import pickle
import mysql.connector
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv()
#simple sql connection using .env for secure info saving
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
SECRET_KEY = os.getenv("SECRET_KEY").encode()
f = Fernet(SECRET_KEY)
cursor = db.cursor()

def handle_client(conn, addr):
    print(f"connction made with {addr}")
    try:

        data = b""
        #receives the data in pieces because the pic has a lot of data
        while True:
            chunk = conn.recv(4096)
            if not chunk:     # when the client sends shutdown(SHUT_WR)
                break
            data += chunk

        plaintext = f.decrypt(data)
        query, params = pickle.loads(plaintext)
        print(f"Query received- {query}")
        print(f"Parameters received- {params}")

        if query.strip().lower().startswith("select"):
            cursor.execute(query, params)
            results = cursor.fetchall()
            # sends select response back
            response = pickle.dumps(results)
            print(f"Results fetched: {results}")
        else:
            print(f"query- {query}")
            cursor.execute(query, params)
            db.commit()
            response = b"SUCCESS"#sends back if succsesfull

        token = f.encrypt(response)
        conn.sendall(token)
        conn.shutdown(socket.SHUT_WR)#done sending command


    except Exception as e:
        print(f"Debug: Exception occurred: {str(e)}")
        conn.sendall(f"ERROR: {str(e)}".encode())
        conn.shutdown(socket.SHUT_WR)

    finally:
        conn.close()


def start_server():
    #                           =ipv4           =tcp
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))     #}
    server.listen()                    #} listen for all connecting ips that send to port 5000
    print("listening on port 5000")
    while True:
        conn, addr = server.accept()
        # creates a thread of requests and sends them to the handle_client func
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
