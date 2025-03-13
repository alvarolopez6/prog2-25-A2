from datetime import datetime
from user import User


class Freelancer(User):
    def __init__(self, username, nombre, password, email, telefono, habilidades, opiniones=None) -> None:
        super().__init__(username, nombre, password, email, telefono)
        # TODO: Mantener atributos como privados, acceder a ellos a través de métodos
        self.habilidades = habilidades
        self.opiniones = opiniones if opiniones is not None else []
        self.rating = sum(self.opiniones) / len(self.opiniones) if self.opiniones else 0
        self.posts = []

    def agregar_un_post(self, titulo: str, descripcion: str, imagen: str, precio: float) -> None:
        self.posts.append(Oferta(titulo, descripcion, datetime.now(), self.username, imagen, precio))

    def eleminar_un_post(self, titulo_no_deseado: str) -> None:
        if titulo_no_deseado in self.posts:
            self.posts.remove(titulo_no_deseado)
            print(f'El Post titulado: {titulo_no_deseado} ha sido eleminado')
        else:
            print(f'El titulo que introduciste no esta en tus posts')

    def agregar_resenya(self, resenya: str) -> None:
        self.opiniones.append(resenya)
        print("HAS AÑADIDO LA RESEÑA CON")
        self.rating = sum(self.opiniones) / len(self.opiniones)

    def mostrar_info(self) -> None:
        super().mostrar_info()
        print(f'Habilidades: {self.habilidades}')
        print(f'Rating: {self.rating}')
        print(f'NºPosts: {len(self.posts)}')

    # METODO:NECESITA CONTRATAR UNA DEMANDA
