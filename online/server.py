import socket
import threading


def listener(_client_socket, _friend_socket):
    try:
        while True:
            data = _client_socket.recv(1024)
            _friend_socket.sendall(data)
    except Exception as e:
        print(e)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8008))
server_socket.listen()

clients = []
print("Сервер запущен и ожидает подключений...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Подключение установлено с {client_address}")
    clients.append((client_socket, True))

    free = [i for i, cl in enumerate(clients) if cl[1]]
    if len(free) > 1:
        clients[free[0]] = (clients[free[0]][0], False)
        clients[free[1]] = (clients[free[1]][0], False)
        clients[free[0]][0].send('init'.encode())
        threading.Thread(target=listener, args=(clients[free[0]][0], clients[free[1]][0]), daemon=True).start()
        threading.Thread(target=listener, args=(clients[free[1]][0], clients[free[0]][0]), daemon=True).start()
