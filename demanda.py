from publicaciones import Publicacion
from typing import Optional

class Demanda(Publicacion):
    def __init__(self, titulo:str, descripcion:str, fecha_publicacion:str, usuario: str, imagen: Optional[str], urgencia:int)->None:
        super().__init__(titulo, descripcion, fecha_publicacion, usuario, imagen)
        self.urgencia = urgencia

    def mostrar_informacion(self) -> str:
        info_base = super().mostrar_informacion()
        return f'{info_base}, Urgencia: {self.urgencia}'