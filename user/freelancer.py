from typing import Self

from .user import User
from post.demand import Demand
from file_utils import PDFFile, PDFFreelancer, XMLFile, Path

from db import SixerrDB, Database

def _init(_self, db) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    _self.__dict__['demandas_contratadas']: set[Demand] = set()
    for post in db.retrieve(Demand, {'contractor': SixerrDB().get_user(_self)}):
        _self.__dict__['demandas_contratadas'].add(post)

    if ('opiniones' in _self.__dict__) and (_self.__dict__['opiniones']):
        _self.__dict__['opiniones'] = list(_self.__dict__['opiniones'])
    else:
        _self.__dict__['opiniones'] = []

def _store(_self, db) -> None:
    """
    Stores the object's attributes which do not fit in usual table columns
    """
    for demanda in _self.demandas_contratadas:
        db.store(demanda)

@Database.register(
    db=SixerrDB(),
    table='freelancers',
    map={
        'rating':'rating',
        'opinions':'opiniones',
        'abilities':'habilidades'
    },
    init=_init, store=_store
)
class Freelancer(User):
    """
        Clase that represent the freelancer, who are the users which have the abilities to offer a job in exchange of
        money

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
        habilidades: list[str]
            a list with all the perks that the freelancer have
        opiniones: list[int]
            a list of numbers that represent the ratings of the customers
        demandas_contratadas: set[Demand]
            a list that contains the Demands accepted, the services will be added through the contratar_demand method
        rating: int
            a number that represent the mean of all the opinions
        posts: list[Oferta]
            a list that includes objects from Oferta class that represent his publications

        Methods
        ---------
        agregar_resenya(resenya:int) -> None
            A method that allows you to append a new rating and calculate again the new rating mean

        contratar_demanda(self,demanda) -> None
            A Method that allows to accept a demand from a costumer

        mostrar_info() -> None
            Display the full public information about the freelancer
        """


    def __init__(self, username:str, nombre:str, password:str, email:str, money:float = 0,telefono:str=None, habilidades:list[str]=None, opiniones: list[int]=None) -> None:
        """
            Initializes a Freelancer instance

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
            habilidades: list[str]
                a list with all the perks that the freelancer have
            opiniones: list[int]
                a list of numbers that represent the ratings of the customers

        """
        super().__init__(username, nombre, password, email, money, telefono)
        self.habilidades = habilidades
        self.demandas_contratadas: set[Demand] = set()
        self.opiniones = opiniones if opiniones is not None else []
        self.rating = sum(self.opiniones) / len(self.opiniones) if self.opiniones else 0


    def agregar_resenya(self, resenya: int) -> None:
        """
        Method used to add an opinion and create a new mean rating after adding it

        Parameters
        ----------
        resenya:int
            An int Value which will influence in the mean rating

        """
        self.opiniones.append(resenya)
        self.rating = sum(map(lambda x:float(x),self.opiniones)) / len(self.opiniones)

    def mostrar_info(self) -> str:
        """
        Method that uses the super info from User and extend it with its own information
        """
        info=super().mostrar_info()
        return info + f'\nHabilidades: {self.habilidades}\nRating: {self.rating}\nNºPosts: {len(self.posts)}{f'\nOpiniones:{self.opiniones}' if self.opiniones else ''}'

    def export_user_pdf(self, tempdir) -> str:
        f = PDFFile(f'{tempdir}/User.pdf')
        pdf_content = PDFFreelancer(
            username=self.username,
            nombre=self.nombre,
            email=self.email,
            telefono=self.telefono,
            posts=self.posts,
            habilidades=self.habilidades,
            opiniones=self.opiniones,
            rating=self.rating,
            money=self.money
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
            if key == 'type' and value != 'Freelancer':
                raise NotImplementedError('User type is not Freelancer')
            setattr(obj, key, value)

        return obj

    def contratar_demanda(self, demanda):
        """
        A Method that allows to accept a demand from an costumer

        Parameters
        -----------
        demanda: Demand
            An object from class Demand that represents demands
        """
        self.demandas_contratadas.add(demanda)
