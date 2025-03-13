from datetime import datetime
from user import User

class Consumer(User):
    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: int, metodo_de_pago: str,
                 pocket: int=0) -> None:
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        super().__init__(username, nombre, password, email, telefono)
        self.metodo_de_pago = metodo_de_pago
        self.servicios_contratados = []
        self.pocket = pocket
        self.demandas = []

    def agregar_una_demanda(self, titulo: str, descripcion: str, imagen: str, urgencia: int) -> None:
        self.demandas.append(Demanda(titulo, descripcion, datetime.now(), self.username, imagen, urgencia))

    def eleminar_una_demanda(self,titulo_no_deseado: str) -> None:
        if titulo_no_deseado in self.demandas:
            self.demandas.remove(titulo_no_deseado)
            print(f'La demanda titulada: {titulo_no_deseado} ha sido eleminada')
        else:
            print(f'El titulo que introduciste no esta en tus demandas')


# METODO:CONTRATAR UN SERVICIO/POST