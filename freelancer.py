from user import User
from offer import Offer
from demand import Demand

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
        agregar_un_post(titulo: str, descripcion: str, imagen: str, precio: float)-> None
            An Method that creates an object Oferta and adds it to the freelancer posts

        eliminar_un_post( titulo_no_deseado:str ) -> None
            A function that allows you to remove an oferta objects from freelancer's posts through its title

        agregar_resenya(resenya:int) -> None
            A method that allows you to append a new rating and calculate again the new rating mean

        contratar_demanda(self,demanda) -> None
            A Method that allows to accept a demand from a costumer

        mostrar_info() -> None
            Display the full public information about the freelancer
        """


    def __init__(self, username:str, nombre:str, password:str, email:str, telefono:str=None, habilidades:list[str]=None, opiniones: list[int]=None) -> None:
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
            telefono: str
                an int that represents the phone number of users
            habilidades: list[str]
                a list with all the perks that the freelancer have
            opiniones: list[int]
                a list of numbers that represent the ratings of the customers

        """
        super().__init__(username, nombre, password, email, telefono)
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        self.habilidades = habilidades
        self.demandas_contratadas:set[Demand] = set()
        self.opiniones = opiniones if opiniones is not None else []
        self.rating = sum(self.opiniones) / len(self.opiniones) if self.opiniones else 0

    def agregar_un_post(self, titulo: str, descripcion: str, imagen: str, precio: float) -> None:
        """
        A Method that is used to create a post/oferta object and add it directly to the freelancer posts.Works the same
        way as uploading to social media.

        Parameters
        ----------
        titulo : str
            Title of the offer.
        descripcion : str
            Description of the offer.
        imagen : str, optional
            Image associated with the offer.
        precio : float
            Price of the offer.

        Notes
        ------
        It uses the offer class to create posts and then add it to the freelancer posts list

        """
        self.posts.add(Offer(titulo, descripcion, self._username, imagen, precio))

    def eliminar_un_post(self, titulo_no_deseado: str) -> None:
        """
        A function that allows to delete an post from freelancer posts list through the title of the post, through the
        iterative search in posts.

        Parameters
        ----------
        titulo_no_deseado:str
            The title of the offer that will be deleted

        Notes
        ------
            In case of not finding that specific post it will not delete it
        """
        quitado = False
        for i in self.posts:
            if i.title == titulo_no_deseado:
                self.posts.remove(i)
                print(f'El Post titulado: {titulo_no_deseado} ha sido eleminado')
                quitado = True
        if not quitado:
            print(f'El titulo que introduciste no esta en tus posts')


    def agregar_resenya(self, resenya: int) -> None:
        """
        Method used to add an opinion and create a new mean rating after adding it

        Parameters
        ----------
        resenya:int
            An int Value which will influence in the mean rating

        """
        self.opiniones.append(resenya)
        print("HAS AÑADIDO LA RESEÑA CON")
        self.rating = sum(self.opiniones) / len(self.opiniones)

    def mostrar_info(self) -> str:
        """

        Method that uses the super info from User and extend it with its own information

        """
        info=super().mostrar_info()
        return info + f' Habilidades: {self.habilidades} Rating: {self.rating} NºPosts: {len(self.posts)}'

    def contratar_demanda(self,demanda):
        """
        A Method that allows to accept a demand from an costumer

        Parameters
        -----------
        demanda: Demand
            An object from class Demand that represents demands
        """
        self.demandas_contratadas.add(demanda)