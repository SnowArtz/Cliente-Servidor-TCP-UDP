import os
import socket
import hashlib
import threading
import time
import datetime

BUFFER_SIZE = 1024
FILE_PATHS = {"100MB": r"C:\Users\samis\Downloads\100MB.txt",
              "250MB": r"C:\Users\samis\Downloads\250MB.txt"}
HOST = '0.0.0.0'
PORT = 12345
MAX_CONCURRENT_CONNECTIONS = 25
LOG_DIR = "Logs_Servidor"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

ready_clients = []
connected_clients = []


def calculate_hash(file_path):
    file_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(BUFFER_SIZE), b""):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def handle_client(client, address, file_path, log_file):
    global ready_clients, connected_clients, num_clients, send_clients

    send_clients+=1
    print(f"[+] {address} conectado.")
    print(send_clients)
    client.sendall(f"{send_clients} {num_clients}".encode())
    client.recv(BUFFER_SIZE)


    client.sendall(f"{os.path.basename(file_path)} {os.path.getsize(file_path)}".encode())
    client.recv(BUFFER_SIZE)

    file_hash = calculate_hash(file_path)
    client.sendall(file_hash.encode())
    client.recv(BUFFER_SIZE)

    ready_clients.append(client)
    while len(ready_clients) != len(connected_clients) or len(ready_clients)!=num_clients:
        time.sleep(0.5)
    with open(file_path, "rb") as f:
        start_time = time.time()
        for chunk in iter(lambda: f.read(BUFFER_SIZE), b""):
            client.sendall(chunk)
        end_time = time.time()

    transfer_time = end_time - start_time
    success = client.recv(BUFFER_SIZE).decode()

    log_entry = f"Cliente: {address} | Tiempo de transferencia: {transfer_time:.2f}s | Resultado: {success}\n"
    with open(log_file, "a") as log:
        log.write(log_entry)

    client.close()
    print(f"[-] {address} desconectado.")


def start_server(file_path, num_clients):
    global ready_clients, connected_clients, send_clients
    ready_clients = []
    connected_clients = []
    send_clients = 0
    log_file = os.path.join(LOG_DIR, f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-log.txt")
    with open(log_file, "a") as log:
        log.write(f"Archivo enviado: {os.path.basename(file_path)} | Tamaño: {os.path.getsize(file_path)}\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(num_clients)

    for _ in range(num_clients):
        client, address = server.accept()
        connected_clients.append(client)
        client_thread = threading.Thread(target=handle_client, args=(client, address, file_path, log_file))
        client_thread.start()

    for client_thread in threading.enumerate():
        if client_thread is not threading.currentThread():
            client_thread.join()

    server.close()


if __name__ == "__main__":
    global num_clients
    while True:
        print("Archivo disponible:")
        for file_key in FILE_PATHS.keys():
            print(f"{file_key}: {FILE_PATHS[file_key]}")

        file_key = input("Seleccione el archivo a enviar (100MB/250MB): ")
        if file_key not in FILE_PATHS:
            print("Seleccion incorrecta. Inténtalo de nuevo.")
            continue
        num_clients = int(input("Ingrese el número de clientes a los que desea enviar el archivo: "))
        if num_clients > MAX_CONCURRENT_CONNECTIONS:
            print(f"El máximo de conexiones concurrentes es {MAX_CONCURRENT_CONNECTIONS}. Inténtalo de nuevo.")
            continue

        start_server(FILE_PATHS[file_key], num_clients)
        user_input = input("¿Desea realizar otra prueba? (s/n): ")
        if user_input.lower() != "s":
            break

