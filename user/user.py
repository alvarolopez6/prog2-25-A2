from utils import crypto as cy
from abc import ABC, abstractmethod
from typing import Self
import multiprocessing as mp
import tempfile
import zipfile
from post.generic_posts import Post
from file_utils import CSVFile, Path, XMLFile
from datetime import datetime
from db import SixerrDB, Database

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except ImportError:
    compression = zipfile.ZIP_STORED

modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}

def _init(_self, _) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    User.usuarios[_self._username] = _self
    _self.__dict__['posts']: set[Post] = set()

@Database.register(
    db=SixerrDB(),
    table='users',
    map={
        'username': '_username',
        'name': 'nombre',
        'pwd_hash': '_password',
        'email': 'email',
        'money': 'money',
        'phone': 'telefono'
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

    def __init__(self, username: str, nombre: str, password: str, email: str, money: float = 0.0, telefono: str=None) -> None:
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

    def __str__(self) -> str:
        return self.mostrar_info()


    @property
    def username(self):
        """
        Get the username of the user.

        Returns
        -------
        str
            The user's username.
        """
        return self._username

    @property
    def get_telefono(self):
        """
        Get the user's phone number.

        Returns
        -------
        str or None
            The user's phone number as a string of 9 digits, or None if not set.
        """
        return self.telefono

    @get_telefono.setter
    def get_telefono(self, value):
        """
        Set the user's phone number.

        Validates that the phone number is either None or a string of exactly 9 digits.
        Raises a ValueError otherwise.

        Parameters
        ----------
        value : str or None
            The phone number to set.

        Raises
        ------
        ValueError
            If the phone number is not None and does not consist of exactly 9 digits.
        """
        if not ((value is None) or (type(value) == str and len(value) == 9 and value.isdigit())):
            raise ValueError('El telefono debe ser un numero')
        else:
            self.telefono = value

    @classmethod
    def get_user(cls, username: str):
        """
        Retrieve a user instance by username from the class-level user dictionary.

        Parameters
        ----------
        username : str
            The username to look up.

        Returns
        -------
        User or None
            The user instance if found, otherwise None.
        """
        if username in cls.usuarios:
            return cls.usuarios[username]

    @property
    def password(self):
        """
        Get the user's password.

        Returns
        -------
        str
            The user's password (probably hashed).
        """
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

    @staticmethod
    def is_valid(card_num: str, exp_date: str, cvv: str) -> int:
        """
        Function to validate a card info (Card number, Expiration date and CVV)
        Expiration date -> Date given is not the present (MM/YY format)
        CVV -> CVV has 3 or 4 digits
        Card number -> has 15 or 16 digits and Luhn algorithm:
        1- Start from the last digit, and double the value of every second digit
        2- If the result of doubling a number gives a 2-digit number, add the digits of the product (e.g., 12: 1 + 2 = 3)
        3- Sum every final digits
        4- If sum % 10 == 0, card number is valid

        Parameters
        ----------
        card_num : str
            The card number to validate, only numbers.
        exp_date: str
            The expiration date of the card.
        cvv: str
            Card's CVV

        Returns
        -------
        int
            - 0 if card is valid
            - 1 if expiration date is not valid
            - 2 if CVV does not have 3 or 4 digits
            - 3 if card does not pass Luhn algorithm or length is not valid

        Raises
        ------
        ValueError
            If any of the parameters characters are invalid
        """
        if not card_num.isdigit(): raise ValueError('Card number must contain only numbers.')
        if not cvv.isdigit(): raise ValueError('CVV must contain only digits.')

        exp_date = datetime.strptime(exp_date, '%m/%y')
        present = datetime.now()
        if exp_date.month != present.month and exp_date.year != present.year:
            if exp_date.date() < present.date(): return 1

        if len(cvv) not in {3, 4}: return 2

        if len(card_num) not in {15, 16}: return 3
        total = 0
        reverse_card = card_num[::-1]  # Start from last digit
        for i, digit in enumerate(reverse_card):
            n = int(digit)
            if i % 2 == 1:  # Every second digit gets doubled
                n *= 2
                if n > 9:  # n is a 2-digit number?
                    n -= 9
            total += n  # Sum final digit
        return 0 if total % 10 == 0 else 3

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
        Gets user's info and exports it to a ZIP file with a .csv, .pdf, and .xml files inside.

        Returns
        -------
        Path
            System path to the file
        """
        funcs = [self.export_user_csv, self.export_user_pdf, self.export_user_xml]
        proccess: list[mp.Process] = []

        temp_dir = 'data/'

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


    def mostrar_info(self) -> str:
        """
        Displays the complete public information about an account.

        """
        return f'Usuario: {self._username}\nNombre: {self.nombre}\nEmail: {self.email}\nTelefono: {self.telefono}\nDinero: {self.money}'