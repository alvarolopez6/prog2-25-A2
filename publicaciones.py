from abc import ABC, abstractmethod

class Publicacion(ABC):
    def __init__(self, titulo: str, descripcion: str, fecha_publicacion: str, usuario) -> None: # falta definir que usuario es de la clase usuario
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_publicacion = fecha_publicacion
        self.usuario = usuario

    @abstractmethod
    def mostrar_informacion(self) -> str:
        return f'Título: {self.titulo}, Descripción: {self.descripcion}, Fecha de publicación: {self.fecha_publicacion}, Usuario: {self.usuario}'

