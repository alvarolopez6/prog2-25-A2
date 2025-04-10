import socket
import threading

class Client:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        print("Conectado al servidor. Escribe /quit para salir del programa.")

        # Hilo para recibir mensajes
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Bucle principal
        self.run()

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(1024).decode()
                if not msg:
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