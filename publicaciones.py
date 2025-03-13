from abc import ABC, abstractmethod
from typing import Optional

class Publicacion(ABC):
    # Lista de categorías permitidas (puedes modificarla según necesites)
    categorias_permitidas = {
        "Matemáticas", "Ciencias", "Física", "Química", "Biología",
        "Historia", "Geografía", "Literatura", "Arte", "Música",
        "Tecnología", "Informática", "Programación", "Robótica", "Astronomía",
        "Deportes", "Salud", "Filosofía", "Psicología", "Economía"
    }
    '''
    @classmethod
    def nueva_categoria(cls, categoria: str) -> None:
        """Añade una categoría a la lista compartida."""
        if categoria not in cls.categorias_permitidas:
            cls.categorias_permitidas.append(categoria)
    '''

    def __init__(self, titulo: str, descripcion: str, fecha_publicacion: str, usuario) -> None:
    def __init__(self, titulo: str, descripcion: str, fecha_publicacion: str, usuario: str, imagen: Optional[str] = None) -> None:
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_publicacion = fecha_publicacion
        self.usuario = usuario
        self.categorias = set()  # Usamos un set para evitar duplicados

    def agregar_categoria(self, categoria: str) -> None:
        """Añade una categoría si está en la lista de permitidas."""
        if categoria in self.categorias_permitidas:
            self.categorias.add(categoria)
        else:
            print(f'Error: La categoría "{categoria}" no está permitida.')

    def eliminar_categoria(self, categoria: str) -> None:
        """Elimina una categoría si existe."""
        self.categorias.discard(categoria)

    def obtener_categorias(self) -> set:
        """Devuelve el conjunto de categorías."""
        return self.categorias
        self.imagen = imagen

# GESTIONAR LA FECHA DE LA CREACION DEL OBJETO. OPCION 1 CREARLO EN LA CLASE CON ALGUNA FUNCION, OPCION 2
    @abstractmethod
    def mostrar_informacion(self) -> str:
        return f'Título: {self.titulo}, Descripción: {self.descripcion}, Fecha de publicación: {self.fecha_publicacion}, Usuario: {self.usuario}, Categorías: {", ".join(self.categorias) if self.categorias else "Sin categorías"}'