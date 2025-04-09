from flask import Flask, request
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required,get_jwt_identity, get_jwt)
import requests
from user import User
from freelancer import Freelancer
from consumer import Consumer
from crypto import hash_str
#from database import SixerrDB

class WrongPass(Exception):
    def __init__(self,username):
        self.username=username

    def __str__(self):
        return f'Wrong Password For Username: {self.username}'

class RestrictionPermission(Exception):
    def __init__(self,tipo):
        self.tipo=tipo

    def __str__(self):
        return f'No puedes Realizar esta tarea debido a que eres : {self.tipo}'


"""
class DBError(Exception):
    def __init__(self, name: str, *args):
        self.name = name
    def __str__(self):
        return f'Couldn\'t start database {self.name}'
"""

class App:
    def __init__(self):
        self.flask = Flask('sixerr')
        """
        self.db = SixerrDB({})
        """
        self.flask.config["JWT_SECRET_KEY"] = "super-secret"
        self.jwt = JWTManager(self.flask)

    def start(self):
        self.flask.run(debug=True)
        """
        if not self.db.init():
            raise DBError(self.db.name)
        for user in self.db.get_users():
            self.users[user['id']] = User.from_dict(user)
        """

if __name__ == '__main__':
    app = App()
    @app.flask.route('/signup', methods=['POST'])
    def signup():
        account = request.args.get('account')
        if account in User.usuarios.keys():
            return f'Usuario {account} ya existe', 409
        else:
            try:
                password = request.args.get('password')
                if User.secure_password(password):
                    nombre = request.args.get('nombre')
                    email = request.args.get('email')
                    tipo = request.args.get('tipo')
                    if tipo=='Freelancer':
                        Freelancer(account,nombre,password,email)
                        return f'Usuario {account} ha sido registrado como Freelancer con exito', 200
                    elif tipo=='Consumer':
                        Consumer(account,nombre,password,email)
                        return f'Usuario {account} ha sido registrado como Consumer con exito', 200
                    else:
                        return f'Por Favor Introduce un Tipo Correcto:(Freelancer/Consumer)', 404
                else:
                    raise WrongPass(account)
            except WrongPass:
                return f'Por Favor verifica que tu password contiene al menos 8 caracteres, Una mayuscula, una minuscula, un simbolo y un numero',404



    @app.flask.route('/login', methods=['GET'])
    def login() -> tuple:
        usuario=request.args.get('usuario')
        password=request.args.get('password')
        if usuario in User.usuarios.keys() and User.usuarios[usuario].password==hash_str(password):
            return create_access_token(identity=usuario),200
        else:
            return "Usuario o contraseña incorrectos",401

    @app.flask.route('/usuario',methods=['PUT'])
    @jwt_required()
    def actualizar_usuario()-> tuple:
        usuario=get_jwt_identity()
        nombre=request.args.get('nombre')
        email=request.args.get('email')
        telefono=request.args.get('telefono')
        try:
            User.usuarios[usuario].nombre=nombre
            User.usuarios[usuario].email = email
            User.usuarios[usuario].telefono=telefono
            return f'el usuario {usuario} ha cambiado sus datos de manera correcta',200
        except:
            return f'Se ha producido un error',404


    @app.flask.route('/usuario', methods=['GET'])
    @jwt_required()
    def mostrar_usuario_actual() -> tuple:
        usuario = get_jwt_identity()
        try:
            return User.usuarios[usuario].mostrar_info(),200
        except:
            return f'Se ha producido un error al buscar datos de tu usuario',404


    @app.flask.route('/usuario', methods=['DELETE'])
    @jwt_required()
    def borrar_cuenta_actual()-> tuple:
        usuario=get_jwt_identity()
        try:
            if User.usuarios[usuario].posts:
                return f'No se ha Borrado Tu cuenta Debido a que tienes posts',404
            else:
                del User.usuarios[usuario]
                return f'Se ha borrado tu cuenta de forma correcta',200
        except:
            return f'Se Ha producido un error',404


    @app.flask.route('/password', methods=['PUT'])
    @jwt_required()
    def cambiar_password() -> tuple:
        usuario = get_jwt_identity()

        old_pass=request.args.get('oldpass')
        new_pass=request.args.get('newpass')
        try:
            if User.usuarios[usuario].password==hash_str(old_pass) and User.secure_password(new_pass):
                User.usuarios[usuario].password=new_pass
                return f'Se ha cambiado tu password de forma correcta', 200
            else:
                raise(WrongPass(usuario))
        except WrongPass as wrong:
            return f'{wrong}'+f' / O el nuevo password no sigue los creterios establecidos', 404


    @app.flask.route('/metodo_pago', methods=['PUT'])
    @jwt_required()
    def cambiar_metodo_pago()->tuple:
        usuario = get_jwt_identity()
        metodos_pago=["Visa","Paypal","America Express","Pocket","Paysera"]
        try:
            if isinstance(User.usuarios[usuario],Consumer):
                metodo=int(request.args.get('metodo'))
                User.usuarios[usuario].metodo_de_pago=metodos_pago[metodo-1]
                return f'Se Ha cambiado el metodo de pago con existo',200
            else:
                raise RestrictionPermission(type(User.usuarios[usuario]).__name__)
        except RestrictionPermission as restricted:
            return f'{restricted}',404


    app.start()