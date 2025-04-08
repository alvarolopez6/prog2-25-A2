from user import User
from offer import Offer
from demand import Demand


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
        agregar_una_demanda(titulo: str, descripcion: str, imagen: str, urgencia: int) -> None
            A function that creates an object demand and add it to the consumer list of demands

        eliminar_una_demanda(titulo_no_deseado : str) -> None
            Delete a demand from a user list of demands through the title of the demand

        contratar_servicio(post:Offer)->None
            Allows to get a service with is an Offer Object.
        """
    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: str= None, metodo_de_pago: str = None,
                 pocket: int=0) -> None:
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
            telefono: int
                an int that represents the phone number of users
            metodo_de_pago: str
                a preference of way of paying which is set to whether the consumer wants to buy with paypal, credit card...
        """
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        super().__init__(username, nombre, password, email, telefono)
        self.metodo_de_pago = metodo_de_pago
        self.servicios_contratados:set[Offer] = set()
        self.pocket = pocket

    def agregar_una_demanda(self, titulo: str, descripcion: str, imagen: str, urgencia: int) -> None:
        """
        A Method that is used to create a demand object and add it directly to the Consumer's demands list. Works the same
        way as uploading to social media.

        Parameters
        ----------
        titulo : str
            Title of the demand.
        descripcion : str
            Description of the demand.
        imagen : str, optional
            Image associated with the demand (default is None).
        urgencia: int
            Level of urgency (e.g., from 1 to 5, where 5 is the highest urgency).
         """
        self.posts.add(Demand(titulo, descripcion, self._username, imagen, urgencia))

    def eliminar_una_demanda(self, titulo_no_deseado: str) -> None:
        """
        A function that allows to delete a demand from a consumer demand's list through the title of the demand, through the
        iterative search in demands.

        Parameters
        ----------
        titulo_no_deseado:str
            The title of the demand that will be deleted

        Notes
        ------
        In case of not finding that specific demand it will not delete it
        """
        quitado = False
        for i in self.posts:
            if i.title == titulo_no_deseado:
                self.posts.remove(i)
                print(f'La demanda titulada: {titulo_no_deseado} ha sido eleminada')
                quitado = True
        if not quitado:
            print(f'El titulo que introduciste no esta en tus demandas')

    def contratar_servicio(self,post)-> None:
        """
                A Method that allows to accept a demand from an costumer

                Parameters
                -----------
                post: Post
                    An object from class Offer that represents offer
                """
        self.servicios_contratados.add(post)


consumer1=Consumer("juan06","pedro","1234","juanceto07@gmail.com", "78566321", "Visa")