import socket
import hashlib
import os
import time
import datetime


HOST = 'localhost'  
PORT = 12345
BUFFER_SIZE = 1024
DOWNLOAD_DIR = 'ArchivosRecibidos'
LOG_DIR = "Logs_Cliente"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def calculate_hash(file_path):
    file_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(BUFFER_SIZE), b""):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def download_file(client):
    client_info = client.recv(BUFFER_SIZE).decode()
    CLIENT_NUM, CONNECT_NUM = client_info.split()
    client.sendall(b"ACK")

    file_info = client.recv(BUFFER_SIZE).decode()
    file_name, file_size = file_info.split()
    file_size = int(file_size)
    client.sendall(b"ACK")

    file_hash = client.recv(BUFFER_SIZE).decode()
    client.sendall(b"ACK")

    download_path = os.path.join(DOWNLOAD_DIR, f"Cliente-{CLIENT_NUM}-Prueba-{CONNECT_NUM}.txt")
    with open(download_path, "wb") as f:
        bytes_received = 0
        start_time = time.time()
        while bytes_received < file_size:
            chunk = client.recv(min(BUFFER_SIZE, file_size - bytes_received))
            bytes_received += len(chunk)
            f.write(chunk)
        end_time = time.time()
    
    log_file = os.path.join(LOG_DIR, "Cliente"+str(CLIENT_NUM)+"-"+f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-log.txt")
    with open(log_file, "a") as log:
        log.write(f"Archivo recibido: {file_name} | Tamaño: {os.path.getsize(download_path)}\n")

    return download_path, file_hash, log_file, end_time-start_time

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))


    download_path, received_file_hash, log_file, transfer_time= download_file(client)
    local_file_hash = calculate_hash(download_path)

    if local_file_hash == received_file_hash:
        print("La transferencia del archivo fue exitosa.")
        success = "EXITOSO"
        client.sendall(b"EXITOSO")
    else:
        print("La transferencia del archivo falló.")
        success = "FALLIDO"
        client.sendall(b"FALLIDO")

    client.close()

    with open(log_file, "a") as log:
        log.write(f"Tiempo de transferencia: {transfer_time:.2f}s | Resultado: {success}\n")


if __name__ == "__main__":
    main()
