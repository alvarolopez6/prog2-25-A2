from typing import Self

from .user import User
from post.offer import Offer
from post.generic_posts import Post
from file_utils import PDFFile, PDFConsumer, XMLFile, Path
from db import SixerrDB, Database

def _init(self, _) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    self.servicios_contratados: set[Post] = set()

@Database.register(
    db=SixerrDB(),
    table='consumers',
    map={'payment':'metodo_de_pago'},
    init=_init
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
        self.servicios_contratados: set[Post] = set()

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

    @classmethod
    def import_user_csv(cls, path: str | Path) -> Self:
        pass

    @classmethod
    def import_user_xml(cls, path: str | Path) -> Self:
        f = XMLFile(path)
        obj = cls.__new__(cls)
        for key, value in f.read().items():
            if key == 'type' and value != 'Consumer':
                raise NotImplementedError('User type is not Consumer')
            setattr(obj, key, value)

        return obj
'''
    def mostrar_info(self) -> str:
        """

        Method that uses the super info from User and extend it with its own information

        """
        info=super().mostrar_info()
        return info + f' metodo de pago: {self.metodo_de_pago}'
'''