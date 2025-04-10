


import crypto as cy


from generic_posts import Post

"""
@register(
    table='users',
    map={'username':'_username',
         'name':'nombre',
         'pwd_hash':'_password',
         'email':'email',
         'phone':'telefono'}
)
"""
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
    usuarios: dict ={}


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
        User.usuarios[username]=self
    """
    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key in type(self).__db__['__map__'].values():
            if self in type(self).usuarios:
                db.SixerrDB().store(self)
    """
    @property
    def username(self):
        return self._username

    @property
    def get_telefono(self):
        return self.telefono

    @get_telefono.setter
    def get_telefono(self, value):
        if not((value is None) or ((type(value) == str) and (len(value) == 9) and (value.isdigit()))):
            raise ValueError('El telefono debe ser un numero')
        else:
            self.telefono = value


    @classmethod
    def get_user(cls, username: str):
        if username in cls.usuarios:
            return cls.usuarios[username]

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        """
        A Method that allows you to change password into an hash string system

        Parameters
        ----------
        value:tupla que contiene la contraseña antigua y la contraseña nueva

        Notes
        ------
        The password need to be implemented in hash system
        """
        self._password=cy.hash_str(value)

    @staticmethod
    def valid_email(email: str):
        """
        Validates if a given email address is valid (in syntax).
        Format must be: name@provider.extension

        Parameters
        ----------
        email: str
            Email address to validate.

        Returns
        -------
        bool
            True if email is valid, otherwise raise ValueError
        """
        if '@' not in email or '.' not in email:
            raise ValueError('Error el formato del email debe seguir: name@provider.extension')

        split_email = email.split('@')
        if len(split_email[0]) == 0 or len(split_email[1]) == 0 or len(split_email) != 2:
            raise ValueError('Error el formato del email debe seguir: name@provider.extension')

        split_domain = split_email[1].split('.')
        if len(split_domain[0]) == 0 or len(split_domain[1]) == 0 or len(split_domain) != 2:
            raise ValueError('Error el formato del email debe seguir: name@provider.extension')

    @staticmethod
    def secure_password(password: str) -> bool:
        """
        Validates if a password is secure enough following criteria:
        - At least 8 characters, 1 lowercase letter, 1 uppercase letter, 1 number and 1 special character.
        - At most 64 characters
        - No whitespace characters

        Parameters
        ----------
        password: str
            Password to validate.

        Returns
        -------
        bool
            True if password is secure, False otherwise.
        """
        if not 8 <= len(password) <= 64:
            return False

        if ' ' in password:
            return False

        has_lower = False
        has_upper = False
        has_digit = False
        has_special = False
        special_characters = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

        for char in password:
            if char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char.isdigit():
                has_digit = True
            elif char in special_characters:
                has_special = True

        return has_lower and has_upper and has_digit and has_special



    def mostrar_info(self) -> str:
        """
        Displays the complete public information about an account.

        """
        return f'Usuario: {self._username} Nombre: {self.nombre} Email: {self.email} Telefono: {self.telefono}'