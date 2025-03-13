from datetime import datetime


class User:
    def __init__(self, username, nombre, password, email, telefono, fecha_creacion=datetime.now()):
        self.username = username
        self.nombre = nombre
        self.password = password  # GUARDAR LA CONTRASENA EN FORMATO HASH
        self.email = email
        self.telefono = telefono
        self.fecha_creacion = fecha_creacion

    def cambiar_contrasenya(self, antigua_contrasenya, nueva_contrasenya):
        if antigua_contrasenya == self.password:
            self.password = nueva_contrasenya
            print("Se ha cambiado tu contraseña de manera correcta")
        else:
            print("Por favor introduce tu contraseña antigua de manera correcta")

    def mostrar_info(self):
        print(f'Usuario: {self.username}')
        print(f'Nombre: {self.nombre}')
        print(f'Email: {self.email}')
        print(f'Telefono: {self.telefono}')


class Freelancer(User):
    def __init__(self, username, nombre, password, email, telefono, habilidades, opiniones=None):
        super().__init__(username, nombre, password, email, telefono)
        self.habilidades = habilidades
        self.opiniones = opiniones if opiniones is not None else []
        self.rating = sum(self.opiniones) / len(self.opiniones) if self.opiniones else 0
        self.posts = []

    def agregar_un_post(self, titulo, descripcion, fecha_publicacion, imagen, precio):
        self.posts.append(Oferta(titulo, descripcion, fecha_publicacion, self.username, imagen, precio))

    def eleminar_un_post(self, titulo_no_deseado):
        quitado = False
        for i in self.posts:
            if i.titulo == titulo_no_deseado:
                self.posts.remove(i)
                print(f'El Post titulado: {titulo_no_deseado} ha sido eleminado')
                quitado = True
        if not quitado:
            print(f'El titulo que introduciste no esta en tus posts')

    def agregar_resenya(self, resenya):
        self.opiniones.append(resenya)
        print("HAS AÑADIDO LA RESEÑA CON")
        self.rating = sum(self.opiniones) / len(self.opiniones)

    def mostrar_info(self):
        super().mostrar_info()
        print(f'Habilidades: {self.habilidades}')
        print(f'Rating: {self.rating}')
        print(f'NºPosts: {len(self.posts)}')

    # METODO:NECESITA CONTRATAR UNA DEMANDA


class Consumer(User):
    def __init__(self, username, nombre, password, email, telefono, metodo_de_pago, pocket=0):
        super().__init__(username, nombre, password, email, telefono)
        self.metodo_de_pago = metodo_de_pago
        self.servicios_contratados = []
        self.pocket = pocket
        self.demandas = []

    def agregar_una_demanda(self, titulo, descripcion, fecha_publicacion, imagen, urgencia):
        self.demandas.append(Demanda(titulo, descripcion, fecha_publicacion, self.username, imagen, urgencia))

    def eleminar_una_demanda(self,titulo_no_deseado):
        quitado = False
        for i in self.demandas:
            if i.titulo == titulo_no_deseado:
                self.demandas.remove(i)
                print(f'La demanda titulada: {titulo_no_deseado} ha sido eleminada')
                quitado = True
        if not quitado:
            print(f'El titulo que introduciste no esta en tus demandas')

# METODO:CONTRATAR UN SERVICIO/POST
# IMPORTAR DEMANDA.py y Oferta.py
