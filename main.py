from flask import Flask, request, send_file, Response, jsonify
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt)

from post.demand import Demand
from user import User
from user.admin import Admin
from user.freelancer import Freelancer
from user.consumer import Consumer
from utils.crypto import hash_str
from typing import Any, Union
from post.offer import Offer
from post.generic_posts import Post
from db import SixerrDB
import user as _user

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


class App:
    def __init__(self) -> None:
        self.flask = Flask(__name__)
        self.db = SixerrDB()
        self.db.sinit()
        # Retrieve users
        for utype in (Admin, Consumer, Freelancer):
            for user in self.db.retrieve(utype):
                User.usuarios[user._username]=user

        self.flask.config["JWT_SECRET_KEY"] = "super-secret"
        self.jwt = JWTManager(self.flask)

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        # -> We dont do it as they get saved on creation and edit
        # Store users
        #for user in User.usuarios.values():
        #    self.db.store(user)
        pass

    def run(self, *args, **kwargs):
        self.flask.run(*args, **kwargs)
        self.close()

app = App()

@app.flask.route('/signup', methods=['POST'])
def signup() -> tuple[str, int]:
    """
    Registers a new user, username must be unique and password must be secure enough (see User.secure_password)

    Reads user data (Username, Name, password, email, type) from request arguments.

    Returns
    -------
    Tuple[str, int]
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
    Tuple[Union[str, dict[str, Any]], int]
        (message, status_code) tuple. Status code can be:
            - 200: Successful login and JWT token is created
            - 401: User or password given is incorrect
    """
    usuario=request.args.get('usuario')
    password=request.args.get('password')
    if usuario in User.usuarios.keys() and User.usuarios[usuario].password==hash_str(password):
        status_code = 200 if isinstance(User.usuarios[usuario], Consumer) \
            else 201 if isinstance(User.usuarios[usuario], Freelancer) else 202
        return create_access_token(identity=usuario), status_code
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
            app.db.delete(User.usuarios[usuario])
            suser = User.usuarios[usuario]
            match type(suser):
                case _user.Consumer:
                    for post in suser.servicios_contratados:
                        app.db.delete(post)
                case _user.Freelancer:
                    for post in suser.demandas_contratadas:
                        app.db.delete(post)
            del User.usuarios[usuario]
            return f'Se ha borrado tu cuenta de forma correcta',200
    except Exception as e:
        print(e)
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
        return f'{restricted}',401

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

@app.flask.route('/posts', methods=['POST'])
@jwt_required()
def publicar_offer() -> tuple[str, int]:
    """
    Publishes an Offer post. Requires a JWT Token. Only for Freelancers

    Reads post's data (Title, description, price) from request arguments.

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Post published
            - 404: User is not freelancer
            - 409: Price is not a number
    """
    current_user=get_jwt_identity()
    usuario=User.usuarios[current_user]
    titulo=request.args.get('titulo')
    description=request.args.get('description')
    try:
        if isinstance(usuario, Freelancer):
            Offer(title=titulo, description=description, user=current_user, price=float(request.args.get('price')))
            return f'Se Ha Publicado tu Offer de forma Correcta', 200
        elif isinstance(usuario, Consumer):
            Demand(title=titulo, description=description, user=current_user, urgency=int(request.args.get('urgency')))
            return f'Se Ha Publicado tu Demanda de forma Correcta', 200
        else:
            raise RestrictionPermission(type(usuario).__name__)
    except RestrictionPermission as restricted:
        return f'{restricted}', 401
    except ValueError:
        return f'Introduce por favor el precio en Numero', 409

@app.flask.route('/posts', methods=['GET'])
def ver_publicaciones() -> tuple[str, int]:
    """
    Returns a string with all posts published separated by ';' character.

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Posts given
            - 404: No posts found
    """
    if not Post.posts:
        return f'No Hay posts en este momento', 404
    else:
        posts = set()
        for post in Post.posts.values():
            posts |= post # posts = posts | post
        return ";".join([i.display_information() for i in posts]), 200

@app.flask.route('/posts/user', methods=['GET'])
@jwt_required()
def ver_propias_publicaciones() -> tuple[str, int]:
    """
    Returns a string with all posts published by own User separated by ';' character.

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Posts given
            - 404: No posts found
    """
    current_user = get_jwt_identity()
    if (current_user in Post.posts) and Post.posts[current_user]:
        return ';'.join([i.display_information() for i in Post.posts[current_user]]), 200 # Se puede usar __str__ en vez de display_information
    else:
        return f'User {current_user} no tiene posts en este momento', 404


@app.flask.route('/posts/category', methods=['POST'])
@jwt_required()
def add_category() -> tuple[str, int]:
    """
    Adds Category to own Posts. Requieres a JWT Token.

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Category Added
            - 404: User has no posts, has no post with that title
    """
    current_user = get_jwt_identity()
    titulo = request.args.get('titulo')
    category = request.args.get('categoria')
    try:
        if current_user in Post.posts:
            post_category=Post.get_post(current_user,titulo)
            post_category.add_category(category)
            return f'La Categoria {category} fue agregada de forma exitosa',200
        return f'User {current_user} no tiene posts', 404
    except ValueError as e:
        return f'{e}',404

@app.flask.route('/posts/user', methods=['DELETE'])
@jwt_required()
def borrar_propias_publicaciones() -> tuple[str, int]:
    """
    Deletes an own post by it title. Requieres a JWT Token.

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Post deleted
            - 404: User has no posts to delete or has no post with that title
    """
    current_user = get_jwt_identity()
    titulo = request.args.get('titulo')
    if current_user in Post.posts:
        for post in Post.posts[current_user]:
            if post.title == titulo:
                app.db.delete(post)
                Post.posts[current_user].remove(post)
                if isinstance(post, Offer):
                    del Offer.offer_feed[post.title]
                else:
                    del Demand.demand_feed[post.title]
                if not Post.posts[current_user]:
                    del Post.posts[current_user]

                return f'Post {post.title} deleted for user {current_user}', 200
        return f'User {current_user} has no post with title {titulo} to delete', 404
    return f'User {current_user} has no posts to delete', 404

@app.flask.route('/usuario/hire', methods=['POST'])
@jwt_required()
def contratar_offer() -> tuple[str, int]:
    """
    Lets a Consumer hire a freelancer's offer. Requieres JWT Token (Consumer).

    Gets from request arguments freelancer's user and post's title

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Offer hired
            - 404: User does not exist, offer not found

    """
    current_user = get_jwt_identity()
    tuser = request.args.get('tuser')
    titulo = request.args.get('titulo')
    try:
        if tuser in User.usuarios:
            user = User.usuarios[current_user]

            if isinstance(user, Consumer) and isinstance(User.usuarios[tuser], Freelancer):
                post = Post.get_post(tuser, titulo)
                if isinstance(post, Offer):
                    user.servicios_contratados.add(post)
                    if user.money >= post.price:
                        user.money -= post.price
                        User.usuarios[tuser].money += post.price
                        return f'Added post {tuser}>{titulo} to user {current_user}', 200
                    else:
                        return 'No tienes suficiente saldo', 401
                else:
                    return 'La oferta no existe', 404
            else:
                return 'Tienes que ser Consumer y el usuario Freelancer', 401
        else:
            return 'El usuario que introduciste no esta en nuestros base de datos', 404
    except ValueError as v:
        return f'{v}',404

@app.flask.route('/usuario/hire', methods=['GET'])
@jwt_required()
def ver_contratadas() -> tuple[str, int]:
    """
    Returns a string with all offers hired by an user separated by ';' character.

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: String returned
            - 404/401: User does not exist or is not Consumer
    """
    current_user = get_jwt_identity()
    current_account=User.usuarios[current_user]
    try:
        if isinstance(current_account, Consumer):
            if current_account.servicios_contratados:
                return ';'.join([i.display_information() for i in current_account.servicios_contratados]), 200
            else:
                return 'NO TIENES SERVICIOS CONTRATADOS',404
        else:
            raise RestrictionPermission(type(current_account).__name__)
    except RestrictionPermission as rest:
        return f'{rest}',401

@app.flask.route('/usuario/export/csv', methods=['GET'])
@jwt_required()
def exportar_perfil_csv() -> tuple[Union[Response, int], int]:
    """
    Exports the user's information into a CSV file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
    """
    current_user = get_jwt_identity()
    user = User.usuarios[current_user]
    return send_file(user.export_user_csv('data/')), 200

@app.flask.route('/usuario/export/pdf', methods=['GET'])
@jwt_required()
def exportar_perfil_pdf() -> tuple[Union[Response, int], int]:
    """
   Exports the user's information into a PDF file.

   Returns
   -------
   Tuple[Union[Response, int], int]
       (File, status_code) tuple. Status code can be:
           - 200: File sended
   """
    current_user = get_jwt_identity()
    user = User.usuarios[current_user]
    return send_file(user.export_user_pdf('data/')), 200


@app.flask.route('/usuario/export/xml', methods=['GET'])
@jwt_required()
def exportar_perfil_xml() -> tuple[Union[Response, int], int]:
    """
    Exports a post's information by its title into an XML file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
            - 404: Post not found
    """
    current_user = get_jwt_identity()
    user = User.usuarios[current_user]
    return send_file(user.export_user_xml('data/')), 200


@app.flask.route('/usuario/export/zip', methods=['GET'])
@jwt_required()
def exportar_perfil_zip() -> tuple[Union[Response, int], int]:
    """
    Exports a post's information by its title into an XML file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
            - 404: Post not found
    """
    current_user = get_jwt_identity()
    user = User.usuarios[current_user]
    return send_file(user.export_user()), 200

@app.flask.route('/posts/export/csv', methods=['GET'])
@jwt_required()
def exportar_post_csv() -> tuple[Union[Response, int], int] | tuple[str, int]:
    """
     Exports a post's information by its title into a CSV file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
            - 404: Post not found
    """
    current_user = get_jwt_identity()
    titulo = request.args.get('titulo')
    try:
        post = Post.get_post(current_user, titulo)
        return send_file(post.export_post_csv('data/')), 200 # A lo mejor hay que borrar el archivo después de enviarlo
    except ValueError as e:
        return f'{e}',404

@app.flask.route('/posts/export/pdf', methods=['GET'])
@jwt_required()
def exportar_post_pdf() -> tuple[Union[Response, int], int] | tuple[str, int]:
    """
     Exports a post's information by its title into a PDF file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
            - 404: Post not found
    """
    current_user = get_jwt_identity()
    titulo = request.args.get('titulo')
    try:
        post = Post.get_post(current_user, titulo)
        return send_file(post.export_post_pdf('data/')), 200 # A lo mejor hay que borrar el archivo después de enviarlo
    except ValueError as e:
        return f'{e}',404

@app.flask.route('/posts/export/xml', methods=['GET'])
@jwt_required()
def exportar_post_xml() -> tuple[Union[Response, int], int] | tuple[str, int]:
    """
     Exports a post's information by its title into a XML file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
            - 404: Post not found
    """
    current_user = get_jwt_identity()
    titulo = request.args.get('titulo')
    try:
        post = Post.get_post(current_user, titulo)
        return send_file(post.export_post_xml('data/')), 200 # A lo mejor hay que borrar el archivo después de enviarlo
    except ValueError as e:
        return f'{e}',404

@app.flask.route('/posts/export/zip', methods=['GET'])
@jwt_required()
def exportar_post_zip() -> tuple[Union[Response, int], int] | tuple[str, int]:
    """
     Exports a post's information by its title into a ZIP file.

    Returns
    -------
    Tuple[Union[Response, int], int]
        (File, status_code) tuple. Status code can be:
            - 200: File sended
            - 404: Post not found
    """
    current_user = get_jwt_identity()
    titulo = request.args.get('titulo')
    try:
        post = Post.get_post(current_user, titulo)
        return send_file(post.export_post()), 200 # A lo mejor hay que borrar el archivo después de enviarlo
    except ValueError as e:
        return f'{e}',404


@app.flask.route('/admin', methods=['DELETE'])
@jwt_required()
def admin_user_delete() -> tuple[str, int]:
    """
    A Function that can be only used by Admin to delete any User Account even if he has posts publicated

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: String returned, Operation Completed
            - 401: Restricted Permision (Only for Admins)
    """
    current_user = get_jwt_identity()
    current_account=User.usuarios[current_user]
    usertodelete = request.args.get('user')
    try:
        if not isinstance(current_account,Admin):
            raise RestrictionPermission(type(current_account).__name__)
        elif usertodelete not in User.usuarios:
            return f'No Existe {usertodelete} en nuestra base de datos',404
        else:
            Admin.delete_user(usertodelete)
            return f'The Account {usertodelete} Has been deleted',200
    except RestrictionPermission as e:
        return f'{e}', 401


@app.flask.route('/usuario/hire', methods=['DELETE'])
@jwt_required()
def cancelar_offer() -> tuple[str, int]:
    """
    Lets a Consumer Cancel a freelancer's offer. Requieres JWT Token (Consumer).

    Gets from request arguments freelancer's user and post's title

    Returns
    -------
    Tuple[str, int]
        (message, status_code) tuple. Status code can be:
            - 200: Offer Canceled
            - 404: User does not exist, offer not found

    """
    current_user = get_jwt_identity()
    tuser = request.args.get('tuser')
    titulo = request.args.get('titulo')
    valoracion= request.args.get('valoracion')
    try:
        if tuser in User.usuarios:
            user = User.usuarios[current_user]

            if isinstance(user, Consumer) and isinstance(User.usuarios[tuser], Freelancer):
                post_to_cancel=Post.get_post(tuser, titulo)
                if post_to_cancel in user.servicios_contratados:
                    user.servicios_contratados.remove(post_to_cancel)
                    User.usuarios[tuser].agregar_resenya(valoracion)
                    return f'Offer of {tuser} -> {titulo} Has been deleted from user {current_user}', 200
                else:
                    return f'No Tienes Contratado Este Post',404
            else:
                return 'Tienes que ser Consumer y el usuario Freelancer', 401
        else:
            return 'El usuario que introduciste no esta en nuestros base de datos', 404
    except ValueError as v:
        return f'{v}', 404


@app.flask.route('/feed', methods=['GET'])
def feed() -> tuple[Response, int]:
    """A function that returns a tuple contains dictionary and status code

     Returns
    -------
    Tuple[dict, int]
        (dict, status_code) tuple. Status code can be:
            - 200: Operation succed

    """
    response = {**Offer.offer_feed, **Demand.demand_feed}
    return jsonify(response), 200

@app.flask.route('/money', methods=['PUT'])
@jwt_required()
def deposit() -> tuple[str, int]:
    """A function where you introduce your visa card information
    and verifies if it is authentic in that case it deposit money
    to the user virtual pocket

     Returns
    -------
    Tuple[str, int]
        (str, status_code) tuple. Status code can be:
            - 200: Operation was successful
            - 404: Visa Card Does Not Exist
            - 409: Introduce valor incorrecto

    """
    current_user = get_jwt_identity()
    user = User.usuarios[current_user]
    visa_number=request.args.get('number')
    visa_cvv=request.args.get('cvv')
    visa_exp=request.args.get('exp')
    try:
        quantity=float(request.args.get('quantity'))
        state=User.is_valid(visa_number, visa_exp, visa_cvv)

        state_info = {0: 'Credit card is valid.',
                      1: 'Credit card is expired, or introduced expiration date format is not valid.',
                      2: 'CVV does not have 3 or 4 digits.',
                      3: 'Card number or length is not valid.'}
        state_str = state_info[state]
        if state==0:
            user.money+=quantity
            return f'Se ha añadido {quantity} al usuario {current_user} de forma correcta', 200
        else:
            return state_str,404

    except ValueError as e:
        return f'{e}',409

@app.flask.route('/admin/post', methods=['DELETE'])
@jwt_required()
def admin_delete_post() -> tuple[str, int]:
    """
    Permite a un administrador eliminar un post específico de cualquier usuario.

    Returns
    -------
    Tuple[str, int]
        - 200: Post eliminado con éxito
        - 401: Permiso denegado (no es admin)
        - 404: Usuario o post no encontrado
    """
    current_user = get_jwt_identity()
    current_account = User.usuarios.get(current_user)

    user_target = request.args.get('user')
    titulo = request.args.get('titulo')

    try:
        if not isinstance(current_account, Admin):
            raise RestrictionPermission(type(current_account).__name__)
        if user_target not in User.usuarios:
            return f'No existe el usuario {user_target} en nuestra base de datos', 404
        if not Post.get_post(user_target,titulo):
            return f'El usuario {user_target} no tiene la publicación {titulo}', 404
        else:
            Admin.delete_post(user_target,titulo)
            try:
                del Offer.offer_feed[titulo]
            except Exception:
                del Demand.demand_feed[titulo]
            return f'Se eliminó el post "{titulo}" de {user_target}', 200

    except RestrictionPermission as e:
        return str(e), 401
