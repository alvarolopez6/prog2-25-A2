#este codigo es igual al de USER1 lo he puesto para comprobar el chat entre dos personas

import socket        #permite la comunicacion server-user en red,facilita el envio de mensajes
import threading     #permite realizar otros subprogramas independientemente sin bloquear al principal
import os
'''
The USER1/2 contains the code parts that manages data received (server-client) (receive_mesages()), 
the sent data (client-server) (run()) and also some parts of the code that manages the connection 
server client (__innit__()). For more clarity I suggest to read the coment all over the code.

Authors:Oussama Samrani El Feouaki   
'''
class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host    #define el host del cliente tendra como direccion la local
        self.port = port    #define el puerto del cliente  que tiene que ser identico al del servidor
        '''crear el socket del cliente, AF_INET representa el IPV4 (IP version 4, XXX.XXX.XXXX.XXXX) y SOCK_STREAM
        representa el TCP (Transmission Control Protocol) es el protocolo utilizado para enviar mensajes sin que se 
         pierden '''
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port)) #conecta el cliente al servidor con el host y el puerto
        print("Conectado al servidor. Escribe /quit para salir del programa.")

        #hilo para recibir mensajes, se ejecuta en un hilo porque el metodo receive_messages() toma mucho tiempo
        threading.Thread(target=self.receive_messages, daemon=True).start()

        #llama al metodo run iniciando el bucle principal, ahora el cliente ya puede recibir y enviar mensajes
        self.run()

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(1024).decode() #recibir los datos de maximo tamano 1024 bytes desde el servidor
                if not msg: #si no hay datos entrantes, esto significa que la conexion ya no se realiza
                    print("\nConexión con el servidor cerrada.")
                    os._exit(0) #termina la ejecucion del codigo
                print("\n" + msg, end="> ") #si hay datos, hacemos el print
            except Exception as e: #si ocurre algun error
                print(f"\nError de conexión: {e}") #mensaje de error
                os._exit(1) #terminar la ejecucion

    def run(self):
        try:
            while True:
                command = input("> ").strip() #escribir un mesaje que puede tambien ser un comando de salida
                if command.lower() == "/quit":
                    self.client_socket.send(command.encode()) #en caso de '/quit' (asi se sale del programa) se envia al servidor
                    self.client_socket.close() #se cierra el socket
                    print("Desconectado del servidor.")
                    break
                self.client_socket.send(command.encode()) #en otro caso se realiza solamente el envio
        except Exception as e: #si ocurre algun error
            print(f"Error: {e}") #se hace el print
        finally:
            self.client_socket.close()  #y se cierra el socket

if __name__ == "__main__":
    client = Client()