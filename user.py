import crypto as cy
from generic_posts import Post
from file_utils import CSVFile, Path, XMLFile
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Self
import multiprocessing as mp
import tempfile
import zipfile
from generic_posts import Post
from file_utils import CSVFile, Path
from datetime import datetime
from db.database import Database
from db.sixerr import SixerrDB

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except ImportError:
    compression = zipfile.ZIP_STORED

modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}

def _init(self) -> None:
    User.usuarios[self._username]=self

@Database.register(
    db=SixerrDB(),
    table='users',
    map={
        'username':'_username',
        'name':'nombre',
        'pwd_hash':'_password',
        'email':'email',
        'money':'money',
        'phone':'telefono'
    },
    init=_init
)
class User(ABC):
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
    posts: set[Post]
        an set that contains all the posts publicated by that user

    Class_Attributes
    ----------
    usuarios: dict[username]=Self:
        an dictionary that uses the username as key and the object User as value


    Methods
    ---------
    secure_password() -> Bool:
        Verifies if the password complete certain creiteria
    export_user() -> Path
        Exports all user's information into a CSV file
    valid_email() -> Bool:
        Verifies if the email contains the correct format
    mostrar_info() -> str
        Shows informaion about a specific account
    """
    usuarios: dict ={}


    def __init__(self, username: str, nombre: str, password: str, email: str, money: float = 0.0,telefono: str=None) -> None:
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
        money: float
                a float that stores user's money
        telefono: str
            an int that represents the phone number of users
        """

        self._username = username #Lectura
        self.nombre = nombre
        self._password = cy.hash_str(password) #Escritura
        self.email = email
        self.money = money
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

    def export_user_csv(self, tempdir: str) -> str:
        """
        Gets user's info and exports it to a CSV file.

        Returns
        -------
        str
            Absolute System path to the file
        """
        user_keys: list[str] = [key for key in self.__dict__.keys()]
        user_values: list[str] = [value for key, value in self.__dict__.items()]
        f = CSVFile(f'{tempdir}/User.csv')
        f.write_headers(user_keys)
        f.write(user_values)
        return f.path.absolute

    @abstractmethod
    def export_user_pdf(self, tempdir: str) -> str:
        """
        Gets user's info and exports it to a PDF file. (Must be implemented by subclasses).

        Returns
        -------
        str
            Absolute System path to the file
        """
        pass

    def export_user_xml(self, tempdir: str) -> str:
        """
        Gets user's info and exports it to a XML file.

        Returns
        -------
        str
            Absolute System path to the file
        """
        f = XMLFile(f'{tempdir}/User.xml')
        f.gen_tree('SixerrData')
        f.write({'type': type(self).__name__, **self.__dict__})
        f.indent()
        return f.path.absolute

    def export_user(self) -> str:
        """
        Gets user's info and exports it to a CSV file.

        Returns
        -------
        Path
            System path to the file
        """
        funcs = [self.export_user_csv, self.export_user_xml]
        proccess: list[mp.Process] = []

        temp_dir = tempfile.gettempdir()

        for f in funcs:
            p = mp.Process(target=f, args=(temp_dir,))
            proccess.append(p)
            p.start()

        for p in proccess:
            p.join()

        file_name = f'{self.username}_{datetime.now().strftime("%Y%m%d")}.zip'
        zip_file = Path(f'{temp_dir}/{file_name}')

        with zipfile.ZipFile(zip_file.absolute, 'w') as z:
            z.write(Path(f'{temp_dir}/User.csv').absolute, self.username + '.csv', compress_type=compression)
            z.write(Path(f'{temp_dir}/User.pdf').absolute, self.username + '.pdf', compress_type=compression)
            z.write(Path(f'{temp_dir}/User.xml').absolute, self.username + '.xml', compress_type=compression)

        return zip_file.absolute

    @classmethod
    @abstractmethod
    def import_user_csv(cls, path: str | Path) -> Self:
        pass

    @classmethod
    @abstractmethod
    def import_user_xml(cls, path: str | Path) -> Self:
        pass

    def mostrar_info(self) -> str:
        """
        Displays the complete public information about an account.

        """
        return f'Usuario: {self._username} Nombre: {self.nombre} Email: {self.email} Telefono: {self.telefono}, Dinero: {self.money}'import crypto as cy