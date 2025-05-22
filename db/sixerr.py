from utils.meta import Singleton
from .database import Database
from .schema import Schema

class SixerrDB(Database, metaclass=Singleton):
    """
    Manages the Sixerr SQL database and its schema as a Singleton
    """
    def __init__(self) -> None:
        """
        Sixerr database object constructor
        """
        super().__init__(
            'Sixerr',
            Schema(
                {
                    'name': 'users',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY',)},
                        {'name': 'username', 'type': 'TEXT', 'mods': ('UNIQUE', 'NOT NULL')},
                        {'name': 'name', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                        {'name': 'pwd_hash', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                        {'name': 'email', 'type': 'TEXT', 'mods': ('UNIQUE', 'NOT NULL')},
                        {'name': 'money', 'type': 'INTEGER'},
                        {'name': 'phone', 'type': 'TEXT'},
                        {'name': 'image', 'type': 'BLOB'},
                    )
                },
                {
                    'name': 'consumers',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
                        {'name': 'payment', 'type': 'TEXT'},
                    ),
                    'indexes': (
                        {'name': 'consumer_id', 'unique': True, 'columns': ('id',)},
                    )
                },
                {
                    'name': 'freelancers',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
                        {'name': 'rating', 'type': 'REAL'},
                        {'name': 'opinions', 'type': 'LIST'},
                        {'name': 'abilities', 'type': 'TEXT'},
                    ),
                    'indexes': (
                        {'name': 'freelancer_id', 'unique': True, 'columns': ('id',)},
                    )
                },
                {
                    'name': 'admins',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
                    ),
                    'indexes': (
                        {'name': 'admin_id', 'unique': True, 'columns': ('id',)},
                    )
                },
                {
                    'name': 'posts',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY',)},
                        {'name': 'username', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                        {'name': 'title', 'type': 'TEXT', 'mods': ('UNIQUE', 'NOT NULL',)},
                        {'name': 'fecha', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                        {'name': 'category', 'type': 'TEXT'},
                        {'name': 'description', 'type': 'TEXT'},
                        {'name': 'image', 'type': 'BLOB'},
                    ),
                    'indexes': (
                        {'name': 'posts_id', 'columns': ('id',)},
                    )
                },
                {
                    'name': 'offer',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES posts(id)')},
                        {'name': 'price', 'type': 'INTEGER', 'mods': ('NOT NULL',)},
                        #{'name': 'contractor', 'type': 'INTEGER', 'mods': ('REFERENCES consumers(id)',)},
                    )
                },
                {
                    'name': 'demand',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES posts(id)')},
                        {'name': 'urgency', 'type': 'INTEGER'},
                        #{'name': 'contractor', 'type': 'INTEGER', 'mods': ('REFERENCES freelancers(id)',)},
                    )
                },
                {
                    'name': 'chats',
                    'columns': (
                        {'name': 'user1', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
                        {'name': 'user2', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
                        {'name': 'msg_id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY',)},
                        {'name': 'content', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                        {'name': 'image', 'type': 'BLOB'},
                    )
                }
            )
        )

    def get_user(self, user: 'User') -> int:
        """
        Gets the id of a user from the database

        :param user: ('User') The user to get the id for.
        :returns: (int) The user's id.
        """
        return self.query('SELECT id FROM users WHERE username=?', (user._username,)).fetchone()['id']

if __name__ == '__main__':
    db = SixerrDB()
    db.sinit()