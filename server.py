import socket
import threading
import json
import os

class ClientHandler(threading.Thread):
    def __init__(self, server, client_socket):
        super().__init__()
        self.server = server
        self.client_socket = client_socket
        self.username = None
        self.current_target = None

    def run(self):
        try:
            self.client_socket.send(b"Ingresa tu nombre de usuario: ")
            self.username = self.client_socket.recv(1024).decode().strip()

            # Verificar si el usuario ya está conectado
            if self.server.is_user_connected(self.username):
                self.client_socket.send(b"Error: Ya estas conectado desde otro terminal.\n")
                self.client_socket.close()
                return

            if not self.server.user_exists(self.username):
                self.server.add_user(self.username)

            self.server.add_connection(self.username, self.client_socket)
            self.show_contact_menu()

            while True:
                msg = self.client_socket.recv(1024)
                if not msg:
                    break
                msg = msg.decode().strip()

                # Manejar comandos primero
                if msg == "/salir":
                    if self.current_target:
                        self.current_target = None
                        self.show_contact_menu()
                    continue
                elif msg == "/quit":
                    break  # Salir completamente del programa

                if self.current_target is None:
                    if msg in self.server.get_usernames(exclude=self.username):
                        self.current_target = msg
                        self.show_chat_history()
                        self.client_socket.send(b"Ahora estas chateando con " + msg.encode() + b"\n")
                        self.client_socket.send(b"Escribe tu mensaje (/salir para volver al menu, /quit para salir)\n")
                    else:
                        self.client_socket.send(b"Contacto invalido. Elige de la lista.\n")
                        self.show_contact_menu()
                else:
                    self.server.store_message(self.username, self.current_target, f"{self.username}: {msg}")
                    self.server.send_message(self.username, self.current_target, msg)

        except Exception as e:
            print(f"Error con {self.username}: {e}")
        finally:
            if self.username:  # Solo si el username fue asignado
                self.server.remove_connection(self.username)
            self.client_socket.close()
            print(f"Conexión con {self.username} cerrada.")

    def show_contact_menu(self):
        contactos = self.server.list_users(exclude=self.username)
        self.client_socket.send(b"\n--- Menu de Contactos ---")
        self.client_socket.send(contactos.encode())
        self.client_socket.send(b"Escribe el nombre del contacto para iniciar chat (/quit para salir):\n")

    def show_chat_history(self):
        history = self.server.get_history(self.username, self.current_target)
        if history:
            self.client_socket.send(b"\n--- Historial de mensajes ---")
            for line in history:
                self.client_socket.send(line.encode() + b"\n")
            self.client_socket.send(b"------------------------------\n")
        else:
            self.client_socket.send(b"\nNo hay mensajes anteriores.")

class ChatServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}  # username: socket
        self.lock = threading.Lock()

        # Persistencia
        self.users_file = "usuarios.txt"
        self.history_file = "historial.json"

        self.users = self.load_users()
        self.history = self.load_history()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"📡 Servidor escuchando en {self.host}:{self.port}")

        while True:
            client_socket, _ = self.server_socket.accept()
            handler = ClientHandler(self, client_socket)
            handler.start()

    # --- Usuarios ---
    def add_user(self, username):
        with self.lock:
            self.users.add(username)
            self.save_users()
            print(f"{username} se ha registrado.")

    def user_exists(self, username):
        with self.lock:
            return username in self.users

    def is_user_connected(self, username):
        with self.lock:
            return username in self.connections

    def add_connection(self, username, client_socket):
        with self.lock:
            self.connections[username] = client_socket
            print(f"{username} se ha conectado.")

    def remove_connection(self, username):
        with self.lock:
            if username in self.connections:
                del self.connections[username]
                print(f"{username} se ha desconectado.")

    def list_users(self, exclude=None):
        with self.lock:
            contactos = [user for user in self.users if user != exclude]
            if contactos:
                return "\n".join(contactos) + "\n"
            else:
                return "No hay otros usuarios registrados.\n"

    def get_usernames(self, exclude=None):
        with self.lock:
            return [user for user in self.users if user != exclude]

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                return set(f.read().splitlines())
        return set()

    def save_users(self):
        with open(self.users_file, "w") as f:
            f.write("\n".join(self.users))

    # --- Mensajes ---
    def send_message(self, from_user, to_user, message):
        with self.lock:
            if to_user in self.connections:
                try:
                    full_message = f"{from_user}: {message}\n"
                    self.connections[to_user].send(full_message.encode())
                except:
                    self.connections[to_user].close()
                    del self.connections[to_user]

    def store_message(self, user1, user2, message):
        key = tuple(sorted((user1, user2)))
        key_str = f"{key[0]}|{key[1]}"
        with self.lock:
            if key_str not in self.history:
                self.history[key_str] = []
            self.history[key_str].append(message)
            self.save_history()

    def get_history(self, user1, user2):
        key = tuple(sorted((user1, user2)))
        key_str = f"{key[0]}|{key[1]}"
        with self.lock:
            return self.history.get(key_str, [])

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return json.load(f)
        return {}

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

if __name__ == "__main__":
    server = ChatServer()
    server.start()