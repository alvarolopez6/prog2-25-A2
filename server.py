import socket        #permite la comunicacion server-user en red,facilita el envio de datos, utiliza TCP
import threading     #permite realizar otros subprogramas independientemente sin bloquear al principal
import json          #convertir datos en archivos json
import os            #validar existencia de archivos

'''
The Server contains the code parts that manage the basic interface that the program shows, the data
coming from the user, also manage the connection server-user and user-user.
For more clarity I suggest to read the coments all over the code.

Authors:Oussama Samrani El Feouaki
'''

#la clase hereda de threading.Thread lo que le deja sobre escribir el metodo run, lo que permite la ejecucion en un hilo independiente
class ClientHandler(threading.Thread):
    def __init__(self, server, client_socket):
        super().__init__()
        self.server = server #se obtiene al crear un objeto de la clase posteriormente
        # no se crea el socket porque se obtiene al crear un objeto de la clase posteriormente
        self.client_socket = client_socket
        self.username = None  #nombre de usuario, es NONE por ahora
        self.current_target = None #nombre del destinario, se define por el usuario

    def run(self): #metodo sobre escrito
        try:
            #pedir al usuario su nombre de usuario y recibirlo en el client_socket
            self.client_socket.send(b"Ingresa tu nombre de usuario: ")
            self.username = self.client_socket.recv(1024).decode().strip()

            if self.server.is_user_connected(self.username): #si el usuario esta conectado ya
                #se muestra un mensaje al cliente y se cierra su session
                self.client_socket.send(b"Error: Ya estas conectado desde otro terminal.\n")
                self.client_socket.close()
                return

            #user_exists() y add_user() son metodos creados posteriormente
            if not self.server.user_exists(self.username): #si el username todavia no existe
                self.server.add_user(self.username) #se anade a los users

            #anadir la conexion({username:socket}) al diccionario de conexiones
            #el diccionario contiene los usuarios conectados en dicho momento
            self.server.add_connection(self.username, self.client_socket)

            #mostrar los contactos con quien el usuario pueda chatear
            self.show_contact_menu()

            #cuando el usuario permanece conectado
            while True:
                msg = self.client_socket.recv(1024) #recibir datos/mensaje del usuario
                if not msg:
                    break
                msg = msg.decode().strip()  #decodificar el mensaje


                if msg == "/salir":         #'/salir' es el comando para salir de una conversacion
                    #si todavia no se ha identificado el destinario mostramos los contactos
                    if self.current_target:
                        self.current_target = None
                        self.show_contact_menu()
                    continue
                elif msg == "/quit":        #'/quit' es el comando de salir del programa (terminar la ejecucion)
                    break  #salir completamente del programa

                #si todavia no se ha definido el destinario, se obtiene desde el dato que envia el usuario
                if self.current_target is None:
                    #si el nombre introducido esta entre los nombres de usuarios
                    if msg in self.server.get_usernames(exclude=self.username):
                        self.current_target = msg   #actualizacion del destinario
                        self.show_chat_history()    #mostrat el historial del chat
                        self.client_socket.send(b"Ahora estas chateando con " + msg.encode() + b"\n")
                        self.client_socket.send(b"Escribe tu mensaje (/salir para volver al menu, /quit para salir)\n")

                    #si el nombre introducido no esta entre los nombres de usuarios
                    else:
                        #se envia un mensaje de fallo
                        self.client_socket.send(b"Contacto invalido. Elige de la lista.\n")
                        #mostrar de nuevo los contactos
                        self.show_contact_menu()
                #si ya tenemos al destinario
                else:
                    #se llaman los metodos store_message() (para guardar el mensaje) y send_message() (para enviarlo)
                    self.server.store_message(self.username, self.current_target, f"{self.username}: {msg}")
                    self.server.send_message(self.username, self.current_target, msg)

        except Exception as e:
            print(f"Error con {self.username}: {e}")

        #manejo del cierro de conexion
        finally:
            if self.username:  #si el username fue asignado
                self.server.remove_connection(self.username) #se quita de las conexiones
            self.client_socket.close() #cerrar el socket
            print(f"Conexión con {self.username} cerrada.")

    #metodo que muestra los contactos
    def show_contact_menu(self):
        contactos = self.server.list_users(exclude=self.username) #se asigna a contactos los contactos
        self.client_socket.send(b"\n--- Menu de Contactos ---")
        self.client_socket.send(contactos.encode())     #mostrar los contactos
        #pedir al usuario escribir el nombre del usuario con quien quiere chatear
        self.client_socket.send(b"Escribe el nombre del contacto para iniciar chat (/quit para salir):\n")

    #metodo que muestra los mensaje antiguos
    def show_chat_history(self):
        #se asigna a history la lista de mensajes (['persona:mensaje',...])
        history = self.server.get_history(self.username, self.current_target)
        if history: #si existen mensajes antiguos
            self.client_socket.send(b"\n--- Historial de mensajes ---")
            for line in history:
                #se muestra cada mensaje
                self.client_socket.send(line.encode() + b"\n")
            self.client_socket.send(b"------------------------------\n")
        else: #si no hay se escribe que no hay mensajes antiguos
            self.client_socket.send(b"\nNo hay mensajes anteriores.")


class ChatServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host    #se define el host (host local)
        self.port = port    #se define un puerto el que tendran tambien los usuarios
        '''crear el socket del cliente, AF_INET representa el IPV4 (IP version 4, XXX.XXX.XXXX.XXXX) y 
        SOCK_STREAM representa el TCP (Transmission Control Protocol) es el protocolo utilizado para 
        enviar mensajes sin que se pierden '''
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}  #se anaden los usuarios conectados de froma {'username': socket,...}
        '''python no puede ejecutar varios programas a la vez, a parte de crear hilos que son subprogramas
        independientes, tambien se pueden causar problemas si los hilos trabajan con los mismos archivos
        el Lock() nos permite bloquear el acceso hasta que termine la ejecucion del hilo 
        '''
        self.lock = threading.Lock()
        self.users_file = "usuarios.txt" #el file que contiendra los nombres de los usuarios
        self.history_file = "historial.json" #el file que contendra el historial de menajes
        self.users = self.load_users() #se llama el metodo de cargar usuarios posteriormente creado
        self.history = self.load_history() #se llama el metodo de cargar el historial posteriormente creado

    #iniciar el servidor
    def start(self):
        #asocia al servidor el host, el puerto y lo inicia
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen() #el servidor esta listo y escuchando conexiones entrantes
        print(f"📡 Servidor escuchando en {self.host}:{self.port}")

        while True:
            client_socket, _ = self.server_socket.accept() #el accept nos da el socket del cliente y su IP
            '''crear el objeto handler y iniciar el bucle principal, ahora los usuarios se conectan y
            se muestra la interfaz basica
            '''
            handler = ClientHandler(self, client_socket)
            handler.start()

    #metodo para anadir usuarios
    def add_user(self, username):
        with self.lock: #activar el bloque
            self.users.add(username)
            self.save_users()
            print(f"{username} se ha registrado.")

    #metodo para verificar si el nombre de usuario ya existe
    def user_exists(self, username):
        with self.lock:
            return username in self.users

    #verificar si el usuario esta conectado
    def is_user_connected(self, username):
        with self.lock:
            return username in self.connections

    #anadir conexiones al diccionario 'connections'
    def add_connection(self, username, client_socket):
        with self.lock:
            self.connections[username] = client_socket
            print(f"{username} se ha conectado.")

    #eliminar conexiones del diccionario 'connections'
    def remove_connection(self, username):
        with self.lock:
            if username in self.connections:
                del self.connections[username]
                print(f"{username} se ha desconectado.")

    #este metodo devuelve los usuarios
    def list_users(self, exclude=None):
        with self.lock:
            contactos = [user for user in self.users if user != exclude]
            if contactos:
                return "\n".join(contactos) + "\n"
            else:
                return "No hay otros usuarios registrados.\n"

    #este metodo devuelve una lista de usuarios
    def get_usernames(self, exclude=None):
        with self.lock:
            return [user for user in self.users if user != exclude]

    #devuelve los usuarios sin repiticon (una set(usuarios))
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                return set(f.read().splitlines())
        return set()

    #guarda los usuarios en el archivo correspondiente
    def save_users(self):
        with open(self.users_file, "w") as f:
            f.write("\n".join(self.users))

    #maneja el envio de mensajes
    def send_message(self, from_user, to_user, message):
        with self.lock:
            if to_user in self.connections: #si el destinario esta en el diccionario
                try:
                    full_message = f"{from_user}: {message}\n"
                    self.connections[to_user].send(full_message.encode()) #envia el mensaje a su socket
                except: #si ocurre algun error
                    self.connections[to_user].close() #se cierra el socket del destinario
                    del self.connections[to_user] #se elimina de la lista de connectados

    #almacenamiento de los mensajes
    def store_message(self, user1, user2, message):
        key = tuple(sorted((user1, user2))) #se crea una tupla universal(cada 2 usuarios tendran la misma) ('bob','carlos')
        key_str = f"{key[0]}|{key[1]}" #'bob|carlos'
        with self.lock:
            if key_str not in self.history: #si todavia no existe un historial de los 2 usuarios
                self.history[key_str] = [] #se crea un diccionario '{'bob|carlos':[mensajes]}'
            self.history[key_str].append(message) #anadir los mensajes
            self.save_history() #guardar en historial

    #obtener el historial, devuelve la lista de mensajes
    def get_history(self, user1, user2):
        key = tuple(sorted((user1, user2)))
        key_str = f"{key[0]}|{key[1]}"
        with self.lock:
            return self.history.get(key_str, [])

    #devuelve el historial tal y como esta
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                return json.load(f)
        return {}

    #guarda el historial
    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

#inicio del srvidor
if __name__ == "__main__":
    server = ChatServer()
    server.start()