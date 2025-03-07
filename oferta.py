from publicaciones import Publicacion

class Oferta(Publicacion):
    def __init__(self, titulo:str, descripcion:str, fecha_publicacion:str, usuario:str, precio:float, disponibilidad:bool)->None:
        super().__init__(titulo, descripcion, fecha_publicacion, usuario)
        self.precio = precio
        self.disponibilidad = disponibilidad

    def mostrar_informacion(self) -> str:
        info_base = super().mostrar_informacion()
        return f'{info_base}, Precio: {self.precio}, Disponibilidad: {self.disponibilidad}'