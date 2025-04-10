import socket        #permite la comunicacion server-user en red,facilita el envio de mensajes
import threading     #permite realizar otros subprogramas independientemente sin bloquear al principal

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
                msg = self.client_socket.recv(1024).decode() #recibir el mensaje de maximo tamano de 1024 bytes desde el servidor
                if not msg: #si no hay mensaje entrante
                    print("\nConexión con el servidor cerrada.")
                    os._exit(0)
                print("\n" + msg, end="> ")
            except Exception as e:
                print(f"\nError de conexión: {e}")
                os._exit(1)

    def run(self):
        try:
            while True:
                command = input("> ").strip()
                if command.lower() == "/quit":
                    self.client_socket.send(command.encode())
                    self.client_socket.close()
                    print("Desconectado del servidor.")
                    break
                self.client_socket.send(command.encode())
        except KeyboardInterrupt:
            print("\nCerrando cliente...")
            self.client_socket.close()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    import os
    client = Client()