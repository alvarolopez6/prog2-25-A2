from publicaciones import Publicacion
from typing import Optional

class Oferta(Publicacion):
    def __init__(self, titulo:str, descripcion:str, fecha_publicacion:str, usuario:str, imagen: Optional[str], precio:float)->None:
        super().__init__(titulo, descripcion, fecha_publicacion, usuario, imagen)
        self.precio = precio

    def mostrar_informacion(self) -> str:
        info_base = super().mostrar_informacion()
        return f'{info_base}, Precio: {self.precio}'