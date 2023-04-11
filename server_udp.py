import socket
import threading
import os
import time

# Configuración
PORT = 12345
BUFFER_SIZE = 8192  # Tamaño máximo de paquete UDP
global NUM_CONCURRENT_CONNECTIONS
FILES = {
    "100MB": r"C:\Users\samis\Downloads\100MB.txt",
    "250MB": r"C:\Users\samis\Downloads\250MB.txt",
}

def send_file(client_address, file_path, log_file):
    print("Sending file to: ", client_address)
    start_time = time.time()
    with open(file_path, "rb") as f:
        for data in iter(lambda: f.read(BUFFER_SIZE), b""):
            server_socket.sendto(data, client_address)
    server_socket.sendto(b"EOF", client_address)  # Send End Of File message
    transfer_time = time.time() - start_time
    log_file.write(f"Cliente: {client_address} | Tiempo de transferencia: {transfer_time:.2f}s\n")


def handle_client(client_address, file_path, log_path):
    global client_num, NUM_CONCURRENT_CONNECTIONS
    client_num+=1
    with open(log_path, "a") as log_file:
        server_socket.sendto(str(client_num).encode(), client_address)  # Send the client_num to the client
        server_socket.sendto(str(NUM_CONCURRENT_CONNECTIONS).encode(), client_address)  # Send the client_num to the client
        send_file(client_address, file_path, log_file)

    data, _ = server_socket.recvfrom(BUFFER_SIZE)
    if data.decode() == "disconnect":
        print(f"Cliente desconectado: {client_address}")
        global disconnected_clients
        disconnected_clients += 1
        if disconnected_clients == NUM_CONCURRENT_CONNECTIONS:
            print("Todos los clientes se han desconectado. Finalizando el programa.")
            os._exit(0)

def main():
    global server_socket, disconnected_clients, client_num, NUM_CONCURRENT_CONNECTIONS
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", PORT))

    selected_file = input("Seleccione el archivo a enviar (100MB/250MB): ")
    file_path = FILES[selected_file]
    
    NUM_CONCURRENT_CONNECTIONS = int(input("Ingrese la cantidad de usuarios a esperar antes de enviar el archivo: "))
    print(f"Servidor listo para enviar {file_path}")
    connections = []
    disconnected_clients = 0
    client_num = 0
    while len(connections) < NUM_CONCURRENT_CONNECTIONS:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        if data.decode() == "connect":
            connections.append(addr)
            print(f"Cliente conectado: {connections[-1]}")

    print("Se alcanzó la cantidad de usuarios esperados. Enviando archivo a todos los clientes.")
    for i in range(len(connections)):
        log_filename = f"Logs_Servidor/{time.strftime('%Y-%m-%d-%H-%M-%S')}-log.txt"
        os.makedirs("Logs_Servidor", exist_ok=True)
        with open(log_filename, "a") as log_file:
            log_file.write(f"Archivo enviado: {os.path.basename(file_path)} | Tamaño: {os.path.getsize(file_path)}\n")
        threading.Thread(target=handle_client, args=(connections[i], file_path, log_filename)).start()



if __name__ == "__main__":
    main()
