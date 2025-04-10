from flask import Flask, request
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt)
import requests
from user import User
from freelancer import Freelancer
from consumer import Consumer
from crypto import hash_str
from typing import Any, Union
#from database import SixerrDB

class WrongPass(Exception):
    """
    Exception raised when a wrong password is introduced.
    """
    def __init__(self,username):
        self.username=username

    def __str__(self):
        return f'Wrong Password For Username: {self.username}'

class RestrictionPermission(Exception):
    """
    Exception raised when a User tries to do a restricted operation.
    """
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
        for user in self.db.retrieve(Freelancer):
            User.usuarios[user.username]=user
        for user in self.db.retrieve(Consumer):
            User.usuarios[user.username]=user
        """
        self.flask.config["JWT_SECRET_KEY"] = "super-secret"
        self.jwt = JWTManager(self.flask)
    """
    def __del__(self):
        ...
    """
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
    def signup() -> tuple[Union[str, dict[str, Any]], int]:
        """
        Registers a new user, username must be unique and password must be secure enough (see User.secure_password)

        Reads user data (Username, Name, password, email, type) from request arguments.

        Returns
        -------
        Tuple[Union[str, Dict[str, Any]], int]
            (message, status_code) tuple. Status_code can be:
                - 200: Successful registration
                - 409: Username already exists or password is not secure enough
                - 404: Account type does not exist
        """
        account = request.args.get('account')
        if account in User.usuarios.keys():
            return f'Usuario {account} ya existe', 409
        else:
            try:
                password = request.args.get('password')
                if User.secure_password(password):
                    nombre = request.args.get('nombre')
                    email = request.args.get('email')
                    User.valid_email(email)
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
                return f'Por Favor verifica que tu password contiene al menos 8 caracteres, Una mayuscula, una minuscula, un simbolo y un numero',409
            except ValueError as e:
                return f'{e}',409


    revoked_tokens = set()

    @app.flask.route('/login', methods=['GET'])
    def login() -> tuple[str, int]:
        """
        Realizes user's login and generates JWT token

        Reads user data (Username, password) from request arguments. If username exists and password given is the same
        as hashed password stored, JWT token is generated.

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Successful login and JWT token is created
                - 401: User or password given is incorrect
        """
        usuario=request.args.get('usuario')
        password=request.args.get('password')
        if usuario in User.usuarios.keys() and User.usuarios[usuario].password==hash_str(password):
            return create_access_token(identity=usuario),200
        else:
            return "Usuario o contraseña incorrectos",401

    @app.flask.route('/usuario',methods=['PUT'])
    @jwt_required()
    def actualizar_usuario()-> tuple[str, int]:
        """
        Updates user's information. A user can only change his own information. JWT token is required.

        Reads new user's data (Name, Email, phone number) from request arguments.

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Information succesfully updated
                - 409: New data is not valid (e.g. phone number contains non digit characters)
        """
        usuario=get_jwt_identity()
        nombre=request.args.get('nombre')
        email=request.args.get('email')
        telefono=request.args.get('telefono')
        try:
            User.usuarios[usuario].nombre=nombre
            User.valid_email(email)
            User.usuarios[usuario].email = email
            User.usuarios[usuario].get_telefono=telefono
            return f'el usuario {usuario} ha cambiado sus datos de manera correcta',200
        except ValueError as e:
            return f'{e}',409


    @app.flask.route('/usuario', methods=['GET'])
    @jwt_required()
    def mostrar_usuario_actual() -> tuple[str, int]:
        """
        Returns user's information. A user can only see his own information. JWT token is requiered.

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Information gived
                - 404: User not found
        """
        usuario = get_jwt_identity()
        try:
            return User.usuarios[usuario].mostrar_info(),200
        except:
            return f'Se ha producido un error al buscar datos de tu usuario',404


    @app.flask.route('/usuario', methods=['DELETE'])
    @jwt_required()
    def borrar_cuenta_actual()-> tuple[str, int]:
        """
        Deletes a user. A user can only delete his own account. JWT token is required.

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Successful deletion
                - 409: User not deleted, all post must be deleted first
                - 404: User not found
        """
        usuario=get_jwt_identity()
        try:
            if User.usuarios[usuario].posts:
                return f'No se ha Borrado Tu cuenta Debido a que tienes posts',409
            else:
                ### db.delete(User.usuarios[usuario])
                del User.usuarios[usuario]
                return f'Se ha borrado tu cuenta de forma correcta',200
        except:
            return f'Se Ha producido un error',404


    @app.flask.route('/password', methods=['PUT'])
    @jwt_required()
    def cambiar_password() -> tuple[str, int]:
        """
        Changes user's password, verifing first his old password. JWT token is required.

        New password must also be secure enough (see User.secure_password).

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Password changed
                - 404: User not found or password is not secure enough
        """
        usuario = get_jwt_identity()

        old_pass=request.args.get('oldpass')
        new_pass=request.args.get('newpass')
        try:
            if User.usuarios[usuario].password==hash_str(old_pass) and User.secure_password(new_pass):
                User.usuarios[usuario].password=new_pass
                return f'Se ha cambiado tu password de forma correcta', 200
            else:
                raise WrongPass(usuario)
        except WrongPass as wrong:
            return f'{wrong}'+f' / O el nuevo password no sigue los creterios establecidos', 404


    @app.flask.route('/metodo_pago', methods=['PUT'])
    @jwt_required()
    def cambiar_metodo_pago() -> tuple[str, int]:
        """
        Changes payment method of own user. JWT Token is required.

        User must be from 'Consumer' type, if not RestrictionPermission Exception is raised.

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Payment method changed
                - 404: RestrictionPermission is raised
        """
        usuario = get_jwt_identity()
        metodos_pago=["Visa","Paypal","America Express","Pocket","Paysera"]
        try:
            if isinstance(User.usuarios[usuario],Consumer):
                metodo=int(request.args.get('metodo'))
                User.usuarios[usuario].metodo_de_pago=metodos_pago[metodo-1]
                return f'Se Ha cambiado el metodo de pago con exito',200
            else:
                raise RestrictionPermission(type(User.usuarios[usuario]).__name__)
        except RestrictionPermission as restricted:
            return f'{restricted}',404

    @app.flask.route('/logout', methods=['DELETE'])
    @jwt_required()
    def logout() -> tuple[str, int]:
        """
        Revokes a JWT token, making a logout.

        Reads JWT token from request argument and adds it's JTI to 'revoked_tokens' set to mark it as revoked.

        Returns
        -------
        Tuple[str, int]
            (message, status_code) tuple. Status code can be:
                - 200: Logout successful
        """
        jti = get_jwt()["jti"]
        revoked_tokens.add(jti)
        return 'Token revocado', 200

    @app.jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header: dict[str, Any], jwt_payload: dict[str, Any]) -> bool:
        """
        Verifies if a token is revoked.

        Checks in 'revoked_tokens' (indentified by JTI) if a token is revoked.

        Parameters
        ----------
        jwt_header: dict[str, Any]
            Header of JWT token
        jwt_payload: dict[str, Any]
            Payload of JWT token, including JTI

        Returns
        -------
        bool
            True if token is revoked, False otherwise
        """
        return jwt_payload["jti"] in revoked_tokens

    app.start()