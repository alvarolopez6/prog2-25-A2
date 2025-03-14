from publicaciones import *
from typing import Optional

class Oferta(Publicacion):
    def __init__(self, titulo:str, descripcion:str, usuario:str, imagen: Optional[str], precio:float,fecha_publicacion: str = datetime.now().date())->None:
        super().__init__(titulo, descripcion, usuario, imagen, fecha_publicacion)
        self.precio = precio

    def mostrar_informacion(self) -> str:
        info_base = super().mostrar_informacion()
        return f'{info_base}, Precio: {self.precio}'