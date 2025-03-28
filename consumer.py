from datetime import datetime
from user import User

class Consumer(User):
    """
        Clase that represent the consumers, which they negotiate with the freelancers and buy offers, services (posts) in
        exchange of money

        Attributes
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
        fecha_creacion: str
            an date that provides information about the time of the creation of certain account
        metodo_de_pago: str
            a preference of way of paying which is set to whether the consumer wants to buy with paypal, credit card...
        servicios_contratados: set[Offer]
            a list that contains the services bought, the services will be added through the contratar_servicios method
        pocket: int
            an int that represent the virtual pocket of an consumer (default 0)
        demandas: set[Offer]
            a list that contains all demands of a certain User


        Methods
        ---------
        agregar_una_demanda(titulo: str, descripcion: str, imagen: str, urgencia: int) -> None
            A function that creates an object demand and add it to the consumer list of demands

        eliminar_una_demanda(titulo_no_deseado : str) -> None
            Delete a demand from a user list of demands through the title of the demand
        """
    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: int, metodo_de_pago: str,
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
        super().__init__(username, nombre, cy.hash_str(password), email, telefono)
        self.metodo_de_pago = metodo_de_pago
        self.servicios_contratados:set[Offer] = set()
        self.pocket = pocket
        self.demandas: set[Offer] = set()

    def agregar_una_demanda(self, titulo: str, descripcion: str, imagen: str, urgencia: int, publication_date:str=datetime.now().date()) -> None:
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
        publication_date:str
            a date when the demand was made (default is the current date)
         """
        self.demandas.add(Demand(titulo, descripcion, self.username, imagen, urgencia, publication_date))

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
        for i in self.demandas:
            if i.titulo == titulo_no_deseado:
                self.demandas.remove(i)
                print(f'La demanda titulada: {titulo_no_deseado} ha sido eleminada')
                quitado = True
        if not quitado:
            print(f'El titulo que introduciste no esta en tus demandas')

# METODO:CONTRATAR UN SERVICIO/POST