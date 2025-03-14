from publicaciones import *
from typing import Optional

class Demanda(Publicacion):
    def __init__(self, titulo:str, descripcion:str, usuario: str, imagen: Optional[str], urgencia:int,fecha_publicacion: str = datetime.now().date())->None:
        super().__init__(titulo, descripcion, usuario, imagen, fecha_publicacion)
        self.urgencia = urgencia

    def mostrar_informacion(self) -> str:
        info_base = super().mostrar_informacion()
        return f'{info_base}, Urgencia: {self.urgencia}'