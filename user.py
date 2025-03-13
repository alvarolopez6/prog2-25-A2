from datetime import datetime

class User:
    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: int) -> None:
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        self.username = username
        self.nombre = nombre
        self.password = password  # GUARDAR LA CONTRASENA EN FORMATO HASH
        self.email = email
        self.telefono = telefono
        self.fecha_creacion = datetime.now()

    def cambiar_contrasenya(self, antigua_contrasenya: str, nueva_contrasenya: str) -> None:
        if antigua_contrasenya == self.password:
            self.password = nueva_contrasenya
            print("Se ha cambiado tu contraseña de manera correcta")
        else:
            print("Por favor introduce tu contraseña antigua de manera correcta")

    def mostrar_info(self) -> None:
        print(f'Usuario: {self.username}')
        print(f'Nombre: {self.nombre}')
        print(f'Email: {self.email}')
        print(f'Telefono: {self.telefono}')

# IMPORTAR DEMANDA.py y Oferta.py
