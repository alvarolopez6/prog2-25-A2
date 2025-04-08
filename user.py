
from ipywidgets import Password

import crypto as cy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from typing import Self

from generic_posts import Post


class WrongPass(Exception):
    def __init__(self,username):
        self.username=username

    def __str__(self):
        return f'Wrong Password For Username:{self.username}'


@register(
    table='users',
    map={'username':'_username',
         'name':'nombre',
         'pwd_hash':'_password',
         'email':'email',
         'phone':'telefono'}
)
class User:
    """
    Main Clase to represent an User

    Attributes
    ----------
    _username: str
        an unique string used to identify objects from others
    nombre: str
        the name of the user
    _password: str
        an unique code that allows you to access to a certain account
    email: str
        a string which provides more information about emails of users
    telefono: str
        an int that represents the phone number of users


    Methods
    ---------
    cambiar_contrasenya(antigua_contrasenya: str ,nueva_contrasenya: str) -> None
        Introduce an old passowrd of an account in order to change it

    mostrar_info() -> None
        Shows informaion about a specific account
    """
    usuarios: dict[str, Self] ={}


    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: str=None) -> None:
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
           telefono: str
                an int that represents the phone number of users

            """
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        self._username = username #Lectura
        self.nombre = nombre
        self._password = cy.hash_str(password) #Escritura
        self.email = email
        self.telefono = telefono
        self.posts: set[Post] = set()
        type(self).usuarios[username]=self

    @property
    def username(self):
        return self._username

    @classmethod
    def get_user(cls, username: str) -> Self | None:
        if username in cls.usuarios:
            return cls.usuarios[username]

    @property
    def password(self):
        raise AttributeError() # Usar error propio WriteOnly

    @password.setter
    def password(self, value: tuple[str, str]) -> None:
        """
        A Method that allows you to change password using your old passowrd as a verificaction of identity
        if the old password introduced not the same as the current one, it wont be changed.

        Parameters
        ----------
        value:tupla que contiene la contraseña antigua y la contraseña nueva

        Notes
        ------
        The password need to be implemented in hash system
        """
        old_pass, new_pass = value[0],value[1]
        if cy.hash_str(old_pass) == self._password:
            self._password = cy.hash_str(new_pass)
            print("Se ha cambiado tu contraseña de manera correcta")
        else:
            raise WrongPass(self._username)


    def login(self,password) -> str:
        if self._password == cy.hash_str(password):
            return create_access_token(identity = self._username)
        else:
            raise WrongPass(self._username)

    @classmethod

    def register(cls, *args, **kwargs):
        cls(*args, **kwargs)


    def mostrar_info(self) -> None:
        """
        Displays the complete public information about an account.

        """
        print(f'Usuario: {self._username}')
        print(f'Nombre: {self.nombre}')
        print(f'Email: {self.email}')
        print(f'Telefono: {self.telefono}')