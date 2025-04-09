import sqlite3 as sql
from typing import Iterable

class Schema:
    """
    Manages a SQL database schema and its relation to a database
    """
    def __init__(self, *tables: dict) -> None:
        """
        Schema object constructor

        :param tables: (*tuple[dict]) Vararg of table dicts
        """
        self.tables = tables

    @staticmethod
    def ctable(table: dict) -> str:
        """
        Construct the SQL table creation query for the table dict

        Table dict format: {
            'name': str,
            'columns': tuple[dict],
            'indexes': *tuple[dict]
        }

        Table > columns dict format: {
            'name': str,
            'type': str,
            'mods': *tuple[str]
        }

        Table > indexes dict format: {
            'name': str,
            'unique': *bool,
            'columns': tuple[str]
        }

        :param table: (dict) Table definition as a dict
        :returns: (str) Constructed SQL table creation query
        """
        # Initialize query
        query = [f'CREATE TABLE {table['name']} (']
        # Loop trough defined columns
        for column in table['columns']:
            # Column creation instruction
            query.append(f'{column['name']} {column['type']}')
            # If modifiers are specified
            for mod in column.get('mods', ()):
                query.append(f' {mod}')
            # Comma separator (gets overwritten)
            query.append(', ')
        # End of definition (overwrites last comma)
        query[-1] = ') STRICT;'
        return ''.join(query)

    @staticmethod
    def cindex(table: dict, index: dict) -> str:
        """
        Construct a SQL index creation query for the table dict

        Table dict format: {
            'name': str,
            'columns': tuple[dict],
            'indexes': *tuple[dict]
        }

        Table > columns dict format: {
            'name': str,
            'type': str,
            'mods': *tuple[str]
        }

        Table > indexes dict format: {
            'name': str,
            'unique': *bool,
            'columns': tuple[str]
        }

        :param table: (dict) Table definition as a dict
        :param index: (dict) Index in the table dict to create query for
        :returns: (str) Constructed SQL index creation query
        """
        # Initialize query
        query = ['CREATE ']
        # If index is unique
        if index.get('unique'):
            query.append('UNIQUE ')
        # Continue query initialization
        query.append(f'INDEX {index['name']} ON {table['name']} (')
        # Loop trough defined columns
        for column in index['columns']:
            # Column index creation instruction
            query.append(column)
            # Comma separator (gets overwritten)
            query.append(', ')
        # End of definition (overwrites last comma)
        query[-1] = ');'
        return ''.join(query)

    def drop(self, db: 'Database') -> bool:
        """
        Drop the schema from a database

        :param db: (Database) Database object to drop the schema from
        :returns: (bool) Whether the operation succeded
        """
        try:
            # Loop trough tables
            for table in self.tables:
                # Create and execute query
                if not db.query(f'DROP TABLE IF EXISTS {table['name']}')[0]:
                    return False # Return if any one fails
                # Loop trough indexes if any
                for index in table.get('indexes', ()):
                    # Create and execute query
                    if not db.query(f'DROP INDEX IF EXISTS {index['name']}')[0]:
                        return False # Return if any one fails
            return True # Return if none fail
        except sql.Error as e:
            print(e)
        return False

    def apply(self, db: 'Database') -> bool:
        """
        Apply the schema to a database

        :param db: (Database) Database object to apply the schema to
        :returns: (bool) Whether the operation succeded
        """
        try:
            # Loop trough tables
            for table in self.tables:
                # Create and execute query
                if not db.query(
                    type(self).ctable(table)
                )[0]:
                    return False # Return if any one fails
                # Loop trough indexes if any
                for index in table.get('indexes', ()):
                    # Create and execute query
                    if not db.query(
                        type(self).cindex(table, index)
                    )[0]:
                        return False # Return if any one fails
            return True # Return if none fail
        except sql.Error as e:
            print(e)
        return False

    def is_active(self, db: 'Database') -> bool:
        try:
            # Loop trough tables
            for table in self.tables:
                # Create and execute query
                res = db.query(f'SELECT count(*) FROM sqlite_master \
                WHERE type=\'table\' AND name=\'{table['name']}\';')
                # Either query failed or table does not exist
                if not (res[0] and res[1].fetchone()[0]):
                    return False # Return if any one fails
            return True # Return if none fail
        except sql.Error as e:
            print(e)
        return False

class Database:
    def __init__(self, id: str, schema: Schema) -> None:
        self.id = id
        self.schema = schema
        self.connection = None

    def __del__(self) -> None:
        self.close()

    @classmethod
    def from_schema(cls, id: str, *tables: dict):
        return cls(id, Schema(*tables))

    def init(self) -> bool:
        # If no possible connection
        if not self.open():
            return False
        # Return status of initializing schema
        return self.schema.drop(self) \
            and self.schema.apply(self)

    def is_init(self) -> bool:
        return self.schema.is_active(self)

    def open(self) -> bool:
        try:
            if not self.connection:
                self.connection = sql.connect(self.id + '.db')
            return True
        except sql.Error as e:
            print(e)
        return False

    def close(self) -> bool:
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
            return True
        except sql.Error as e:
            print(e)
        return False

    def query(self, query: str, parameters: dict | Iterable=()) -> tuple[bool, None | sql.Cursor]:
        if not self.connection:
            return False, None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            return True, cursor
        except sql.Error as e:
            print(e)
        return False, None

class Singleton(type):
    """
    Singleton metaclass

    Enforces the singleton pattern on a class.
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        """
        Construct a class instance following the singleton pattern

        Constructs an instance or returns one if it was already made before.
        """
        if not (cls in type(cls)._instances):
            type(cls)._instances[cls] = super(type(cls), cls).__call__(*args, **kwargs)
        return type(cls)._instances[cls]

class SixerrDB(Singleton, Database):
    instantiated=False

    def __init__(self, schema: Schema) -> None:
        if type(self).instantiated:
            return
        super().__init__('Sixerr', schema)
        type(self).instantiated = True

    def __del__(self) -> None:
        super().__del__()
        type(self).instantiated = False

    def init(self) -> bool:
        if super().is_init():
            return True
        return super().init()

    def add_user(self, dtype: str, username: str, pwd_hash: str, email: str, image: bytes) -> bool:
        if not super().query(
            'INSERT INTO users (username, pwd_hash, email, image) VALUES (?,?,?,?)',
            (username, pwd_hash, email, image)
        )[0]:
            return False

        return super().query(
            f'INSERT INTO {dtype}s (id) VALUES (SELECT id FROM users WHERE username=\'{username}\')'
        )[0]

    def add_post(self, username: str, pwd_hash: str, email: str, image: bytes) -> bool:#######################################################################
        return super().query(
            'INSERT INTO users (username, pwd_hash, email, image) VALUES (?,?,?,?)',
            (username, pwd_hash, email, image)
        )[0]

def main():
    schema = Schema(
        {
            'name': 'users',
            'columns': (
                {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY',)},
                {'name': 'username', 'type': 'TEXT', 'mods': ('UNIQUE', 'NOT NULL')},
                {'name': 'pwd_hash', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                {'name': 'email', 'type': 'TEXT', 'mods': ('UNIQUE', 'NOT NULL')},
                {'name': 'image', 'type': 'BLOB'},
            )
        },
        {
            'name': 'consumers',
            'columns': (
                {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
            ),
            'indexes': (
                {'name': 'consumer_id', 'unique': True, 'columns': ('id',)},
            )
        },
        {
            'name': 'freelancers',
            'columns': (
                {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES users(id)')},
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
                {'name': 'user', 'type': 'INTEGER', 'mods': ('NOT NULL', 'REFERENCES users(id)')},
                {'name': 'title', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                {'name': 'description', 'type': 'TEXT'},
                {'name': 'image', 'type': 'BLOB'},
            ),
            'indexes': (
                {'name': 'posts_user', 'columns': ('user',)},
            )
        }
    )

    db = SixerrDB(schema)
    if not db.init():
        print('Something went wrong')
    print(db.is_init())
    db.schema.drop(db)
    print(db.is_init())


if __name__ == '__main__':
    main()