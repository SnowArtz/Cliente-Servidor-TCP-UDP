import socket
import threading
import os
import sys
import datetime
import time

# Configuración
SERVER_IP = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 8192 
LOG_DIR = "Logs_Cliente"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def receive_file(client_socket):

    client_num_data, _ = client_socket.recvfrom(BUFFER_SIZE)
    CLIENT_NUM = int(client_num_data.decode())
    connect_num_data, _ = client_socket.recvfrom(BUFFER_SIZE)
    CONNECT_NUM = int(connect_num_data.decode())

    os.makedirs("ArchivosRecibidos", exist_ok=True)
    received_file_path = f"ArchivosRecibidos/Client-{CLIENT_NUM}-Prueba-{CONNECT_NUM}.txt"

    with open(received_file_path, "wb") as f:
        start_time = time.time()
        while True:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            if data == b"EOF":  # Close the connection when receiving the End Of File message
                break
            f.write(data)
        end_time = time.time()

    print(f"Archivo recibido: {received_file_path}")
    client_socket.sendto("disconnect".encode(), (SERVER_IP, PORT))  # Send disconnect message

    log_file = os.path.join(LOG_DIR, "Cliente"+str(CLIENT_NUM)+"-"+f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-log.txt")
    with open(log_file, "a") as log:
        log.write(f"Archivo recibido: {received_file_path} | Tamaño: {os.path.getsize(received_file_path)}\n")
        log.write(f"Tiempo de transferencia: {end_time-start_time:.2f}s\n")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto("connect".encode(), (SERVER_IP, PORT))
    threading.Thread(target=receive_file, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
