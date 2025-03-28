from flask import Flask, request
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required,get_jwt_identity, get_jwt)
import requests
from crypto import hash_str
#from database import SixerrDB

class DBError(Exception):
    def __init__(self, name: str, *args):
        self.name = name
    def __str__(self):
        return f'Couldn\'t start database {self.name}'

class App:
    def __init__(self):
        self.flask = Flask('sixerr')
        self.db = SixerrDB({})
        self.flask.config["JWT_SECRET_KEY"] = "super-secret"
        self.jwt = JWTManager(app)

    def start(self):
        self.flask.run(debug=True)
        if not self.db.init():
            raise DBError(self.db.name)
        for user in self.db.get_users():
            self.users[user['id']] = User.from_dict(user)

    @app.route('/signup', methods=['POST'])
    def signup():
        user = request.args.get('user', '')
        if user in users:
            return f'Usuario {user} ya existe', 409
        else:
            password = request.args.get('password', '')
        hashed = hash_str(password)
        users[user] = hashed
        return f'Usuario {user} registrado', 200

if __name__ == '__main__':
    app = App()
    app.start()



