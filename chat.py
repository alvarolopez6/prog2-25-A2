import sqlite3

class User:
    pass

class ChatUser:
    pass

def database_decorator(func):
    def wrapper(self, *args, **kwargs):
        conn = sqlite3.connect('chats.db')
        cursor = conn.cursor()
        result = func(self, *args, **kwargs)
        # Guardar el mensaje en la base de datos (REAL)
        cursor.execute('''
            INSERT INTO mensajes VALUES (?, ?, ?)
        ''', (self.user1.username, self.user2.username, self.msg))
        conn.commit()  # Confirmar cambios
        conn.close()  # Cerrar conexión
        return result
    return wrapper


class Chat(ChatUser):
    @database_decorator
    def __init__(self, user1: User, user2: User, msg: str) -> None:
        if not isinstance(user1,User) or not isinstance(user2,User) or not isinstance(msg,str):
            raise TypeError('Incorrect type of arguments')
        else:
            self.user1 = user1
            self.user2 = user2
            self.msg = msg