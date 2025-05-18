from user import User
from offer import Offer
from generic_posts import Post
from demand import Demand
from db.database import Database
from db.sixerr import SixerrDB

def _init(self) -> None:
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
        pocket: int
            an int that represent the virtual pocket of an consumer (default 0)


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
'''
    def mostrar_info(self) -> str:
        """

        Method that uses the super info from User and extend it with its own information

        """
        info=super().mostrar_info()
        return info + f' metodo de pago: {self.metodo_de_pago}'
'''