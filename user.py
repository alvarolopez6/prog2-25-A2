from datetime import datetime

class User:
    """
    Main Clase to represent an User

    Attributes
    ----------
    username: str
        an unique string used to identify objects from others
    nombre: str
        the name of the user
    password: str
        an unique code that allows you to access to a certain account
    email: str
        a string which provides more information about emails of users
    telefono: int
        an int that represents the phone number of users
    fecha_creacion: str
        an date that provides information about the time of the creation of certain account


    Methods
    ---------
    cambiar_contrasenya(antigua_contrasenya: str ,nueva_contrasenya: str) -> None
        Introduce an old passowrd of an account in order to change it

    mostrar_info() -> None
        Shows informaion about a specific account
    """



    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: int) -> None:
        """
           Initializes an User instance

           Parameters
           ----------
           username: str
                an unique string used to identify objects from others
           nombre: str
                the name of the user
           password: str
                an unique code that allows you to access to a certain account (hash system)
           email: str
                a string which provides more information about emails of users
           telefono: int
                an int that represents the phone number of users

            """
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        self.username = username
        self.nombre = nombre
        self.password = password  # GUARDAR LA CONTRASENA EN FORMATO HASH
        self.email = email
        self.telefono = telefono
        self.fecha_creacion = datetime.now().date()



    def cambiar_contrasenya(self, antigua_contrasenya: str, nueva_contrasenya: str) -> None:
        """
        A Method that allows you to change password using your old passowrd as a verificaction of identity
        if the old password introduced not the same as the current one, it wont be changed.

        Parameters
        ----------
        antigua_contrasenya: str
            The old passowrd that must be in the same as the current to bypass the protection system
        nueva_contrasenya: str
            New password that will be set in case of the verification of the identity

        Notes
        ------
        The password need to be implemented in hash system
        """
        if cy.hash_str(antigua_contrasenya) == self.password:
            self.password = cy.hash_str(nueva_contrasenya)
            print("Se ha cambiado tu contraseña de manera correcta")
        else:
            print("Por favor introduce tu contraseña antigua de manera correcta")




    def mostrar_info(self) -> None:
        """
        Displays the complete public information about an account.

        """
        print(f'Usuario: {self.username}')
        print(f'Nombre: {self.nombre}')
        print(f'Email: {self.email}')
        print(f'Telefono: {self.telefono}')

# IMPORTAR DEMANDA.py y Oferta.py
