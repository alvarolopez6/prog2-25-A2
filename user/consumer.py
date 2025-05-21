from typing import Self

from .user import User
from post.offer import Offer
from post import Offer
from file_utils import PDFFile, PDFConsumer, XMLFile, Path
from db import SixerrDB, Database

def _init(_self: 'Consumer', db: Database) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    _self.__dict__['servicios_contratados']: set[Offer] = set()
    for post in db.retrieve(Offer, {'contractor': SixerrDB().get_user(_self)}):
        _self.__dict__['servicios_contratados'].add(post)

def _store(_self: 'Consumer', db: Database) -> None:
    """
    Stores the object's attributes which do not fit in usual table columns
    """
    for servicio in _self.servicios_contratados:
        db.store(servicio)

@Database.register(
    table='consumers',
    map={'payment':'metodo_de_pago'},
    init=_init, store=_store
)
class Consumer(User):
    """
        Clase that represent the consumers, which they negotiate with the freelancers and buy offers, services (posts) in
        exchange of money

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
        telefono: int
            an int that represents the phone number of users
        metodo_de_pago: str
            a preference of way of paying which is set to whether the consumer wants to buy with paypal, credit card...
        servicios_contratados: set[Offer]
            a list that contains the services bought, the services will be added through the contratar_servicios method
        money: float
            an float that represent the virtual pocket of an consumer (default 0)


        Methods
        ---------

        contratar_servicio(post:Offer)->None
            Allows to get a service with is an Offer Object.

        mostrar_info()->str
            En extended version of User Mostar info method, that shows informations about an consumer
        """
    def __init__(self, username: str, nombre: str, password: str, email: str, money: float = 0,telefono: str= None, metodo_de_pago: str = None) -> None:
        """
            Creates an instance of Consumer

            Parameters
            ----------
            username: str
                an unique string used to identify objects from others
            nombre: str
                the name of the user
            password: str
                an unique code that allows you to access to a certain account
            email: str
                a string which provides more information about emails of users
            money: float
                a float that stores user's money
            telefono: int
                an int that represents the phone number of users
            metodo_de_pago: str
                a preference of way of paying which is set to whether the consumer wants to buy with paypal, credit card...
        """
        super().__init__(username, nombre, password, email, money, telefono)
        self.metodo_de_pago = metodo_de_pago
        self.servicios_contratados: set[Offer] = set()

    def contratar_servicio(self,post)-> None:
        """
        A Method that allows to accept a demand from an costumer

        Parameters
        -----------
        post: Post
            An object from class Offer that represents offer
        """
        self.servicios_contratados.add(post)


    def export_user_pdf(self, tempdir: str) -> str:
        """
        Export the user's data to a PDF file.

        Generates a PDF document containing the user's profile information,
        including contact details, posts, payment method, balance, and contracted services.
        The PDF is saved to the specified temporary directory.

        Parameters
        ----------
        tempdir : str
            Path to the temporary directory where the PDF will be saved.

        Returns
        -------
        str
            Absolute path to the generated PDF file.
        """
        f = PDFFile(f'{tempdir}/Post.pdf')
        pdf_content = PDFConsumer(
            username=self.username,
            nombre=self.nombre,
            email=self.email,
            telefono=self.telefono,
            posts=self.posts,
            metodo_de_pago=self.metodo_de_pago,
            money=self.money,
            servicios_contratados=self.servicios_contratados
        )
        f.write(pdf_content)
        return f.path.absolute

