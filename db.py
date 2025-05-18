import sqlite3 as sql
from os.path import abspath, isdir
from typing import Self, Any, Type, Iterable, Iterator, Callable
from decorators import dec_wparams, readonly, memoize

type Path = str | bytes | os.PathLike[str] | PathLike[bytes]

class DatabaseException(Exception):
    """
    Database base exception class
    """
    def __init__(self, msg: str, *args: Any) -> None:
        """
        Database exception constructor

        :param msg: (str) Error message to show
        :param args: (*Any) Any other arguments
        """
        super().__init__(msg, *args)
        self.msg = msg

    def __str__(self) -> str:
        """
        Gives the string representation of the exception

        :returns: (str) String representation of the exception
        """
        return f'Database Exception: {self.msg}'

class SchemaError(DatabaseException):
    """
    Schema exception class

    Raised when malformed schema definitions get used to create Schema instances
    """
    def __init__(self, e: Exception | str, *args: Any) -> None:
        """
        Schema exception constructor

        :param e: (Exception) Error that caused the exception
        :param args: (*Any) Any other arguments
        """
        super().__init__(f'Schema -> {str(e)}', *args)

class PathError(DatabaseException):
    """
    Path exception class

    Raised when there are problems with a database path
    """
    def __init__(self, e: Exception | str, *args: Any) -> None:
        """
        Path exception constructor

        :param e: (Exception) Error that caused the exception
        :param args: (*Any) Any other arguments
        """
        super().__init__(f'Path -> {str(e)}', *args)

class ConnectionError(DatabaseException):
    """
    Connection exception class

    Raised when there is an error when connection or disconnection from the database
    """
    def __init__(self, e: Exception | str, *args: Any) -> None:
        """
        Connection exception constructor

        :param e: (Exception) Error that caused the exception
        :param args: (*Any) Any other arguments
        """
        super().__init__(f'Connection -> {str(e)}', *args)

class QueryError(DatabaseException):
    """
    Query exception class

    Raised when there is an error when executing a sql query
    """
    def __init__(self, e: Exception | str, query: str, parameters: dict[str, Any] | Iterable, *args: Any) -> None:
        """
        Query exception constructor

        :param e: (Exception) Error that caused the exception
        :param args: (*Any) Any other arguments
        """
        super().__init__(f'Query -> |{query}| < {parameters} -> {str(e)}', *args)

class SubscriptionError(DatabaseException):
    """
    Subscription exception class

    Raised when there is an error related to object subscriptions
    """
    def __init__(self, e: Exception | str, *args: Any) -> None:
        """
        Subscription exception constructor

        :param e: (Exception) Error that caused the exception
        :param args: (*Any) Any other arguments
        """
        super().__init__(f'Subscription -> {str(e)}', *args)

@readonly(attrs={'__tables'})
class Schema:
    """
    Manages a SQL database schema and its relation to a database
    """
    def __init__(self, *tables: dict, check: bool=True) -> None:
        """
        Schema object constructor

        :param tables: (*dict) Vararg of table dicts
        :param check: (bool) Whether to check if the tables are well-formed
        :raises SchemaError: When check is True and the schema is not valid
        """
        if check:
            # Check if schema is valid
            is_valid, fail = type(self).check(tables)
            # Raise error if it is not
            if not is_valid:
                raise SchemaError(fail)
        self.__tables: tuple[dict, ...] = tables

    def __len__(self) -> int:
        """
        Get the length of the schema

        The length of the schema is the number of tables it has defined.

        :returns: (int) The schema length
        """
        return self.__tables.__len__() # Delegates work to dict

    def __eq__(self, other: Self) -> bool:
        """
        Check if two schemas are equal

        Schemas are considered equal if they
        have the same index and table definitions

        :param other: (Self) Other instance to compare to
        :returns: (bool) Whether the two schemas are equal
        """
        return (self.__tables == other.__tables) # Delegates work to dict

    def __bool__(self) -> bool:
        """
        Returns the boolean representation of the schema

        :returns: (bool) Whether the schema is valid or not
        """
        return self.is_valid

    def __str__(self) -> str:
        """
        Get a string representation of the schema

        :returns: (str) String representation of the schema
        """
        return f'<Schema {id(self)}>' # Used for memoize

    @property
    def is_valid(self) -> bool:
        """
        Checks the validity of the schema

        :returns: (bool) Whether the schema is valid or not
        """
        return type(self).check(self.__tables)[0]

    def drop(self, db: 'Database') -> None:
        """
        Drop the schema from a database

        :param db: (Database) Database object to drop the schema from
        :raises ConnectionError: When dropping a schema on a db with no connection
        :raises QueryError: When any query needed to drop the schema fails
        """
        # Loop trough tables
        for table in self.__tables:
            # Create and execute query
            db.query(f'DROP TABLE IF EXISTS {table['name']}')
            # Loop trough indexes if any
            for index in table.get('indexes', ()):
                # Create and execute query
                db.query(f'DROP INDEX IF EXISTS {index['name']}')

    def apply(self, db: 'Database') -> None:
        """
        Apply the schema to a database

        :param db: (Database) Database object to apply the schema to
        :raises ConnectionError: When applying a schema on a db with no connection
        :raises QueryError: When any query needed to apply the schema fails
        """
        # Loop trough tables
        for table in self.__tables:
            # Create and execute query
            db.query(type(self)._ctable(table))
            # Loop trough indexes if any
            for index in table.get('indexes', ()):
                # Create and execute query
                db.query(type(self)._cindex(table, index))

    def is_active(self, db: 'Database') -> bool:
        """
        Check if the schema is applied to a database

        :param db: (Database) Database object to check for
        :raises ConnectionError: When checking if the schema is applied on a db with no connection
        :raises QueryError: When any query needed to check if the schema is applied fails
        """
        # Loop trough tables
        for table in self.__tables:
            # Create and execute query
            cs = db.query(f'SELECT count(*) FROM sqlite_master \
            WHERE type=\'table\' AND name=\'{table['name']}\';')
            # Table does not exist
            if not (cs and cs.fetchone()[0]):
                return False # Return if any one fails
        return True # Return if none fail

    def has_table(self, db: 'Database', name: str) -> bool:
        """
        Check if database and schema have a table

        :param db: (Database) Database object to check on
        :param name: (str) Table name to check for existence
        :raises ConnectionError: When checking table existing on database with no connection
        :raises QueryError: When the query needed to check if the table exists fails
        """
        # Loop trough tables
        for table in self.__tables:
            # If table name is the one we are looking for
            if (table['name'] == name):
                break # Skips else block
        else:
            # Tables exhausted and no name match
            return False
        # Query table existence
        cs = db.query(f'SELECT count(*) FROM sqlite_master \
        WHERE type=\'table\' AND name=\'{name}\';')
        # Table does not exist
        if not (cs and cs.fetchone()[0]):
            return False
        # Table exists
        return True

    @memoize
    def get_nkeys(self, name: str, allow: tuple[str, ...]=(), ignore: tuple[str, ...]=()) -> tuple[str, ...] | None:
        """
        Get the column names of a table

        :param name: (str) Table name to get columns for
        :param allow: (tuple[str, ...]) Tuple of columns to allow
        :param ignore: (tuple[str, ...]) Tuple of columns to ignore
        :returns: (tuple[str, ...] | None) Tuple with column names or None if table not found
        """
        # Loop trough tables
        for table in self.__tables:
            # If table name is the one we are looking for
            if (table['name'] == name):
                cnames = [] # Column name list
                # Loop trough columns
                for column in table['columns']:
                    # Ignore columns
                    if not column['name'] in ignore:
                        if (not allow) or (column['name'] in allow):
                            # Append name to list
                            cnames.append(column['name'])
                return tuple(cnames)

    @memoize
    def get_pkeys(self, name: str, allow: tuple[str, ...]=(), ignore: tuple[str, ...]=()) -> tuple[str, ...] | None:
        """
        Get the column names that are the primary keys of a table

        :param name: (str) Table name to get pkey columns for
        :param allow: (tuple[str, ...]) Tuple of columns to allow
        :param ignore: (tuple[str, ...]) Tuple of columns to ignore
        :returns: (tuple[str, ...] | None) Tuple with pkey column names or None if table not found
        """
        # Loop trough tables
        for table in self.__tables:
            # If table name is the one we are looking for
            if (table['name'] == name):
                cnames = [] # Column name list
                # Loop trough columns
                for column in table['columns']:
                    # Ignore columns
                    if not column['name'] in ignore:
                        if (not allow) or (column['name'] in allow):
                            # If mod is primary key or alternative key
                            if ('PRIMARY KEY' in column.get('mods', ()))\
                                or (('UNIQUE' in column.get('mods', ())) and ('NOT NULL' in column.get('mods', ()))):
                                # Append name to list
                                cnames.append(column['name'])
                return tuple(cnames)

    @memoize
    def get_erefs(self, name: str) -> tuple[tuple[str, str, str], ...] | None:
        """
        Get the table and column names that are the external references of a table

        :param name: (str) Table name to get erefs table and columns for
        :returns: (tuple[tuple[str, str, str], ...] | None) Tuple with table and column names or None if table not found
        """
        # Loop trough tables
        for table in self.__tables:
            # If table name is the one we are looking for
            if (table['name'] == name):
                tcnames = [] # Table and column name list
                # Loop trough columns
                for column in table['columns']:
                    # Loop trough mods
                    for mod in column.get('mods', ()):
                        # If mod is a reference
                        if 'REFERENCES' in mod:
                            # Extract table and column
                            etable, ecolumn = mod[10:].strip().rstrip(')').split('(')
                            # Append table and column names to list
                            tcnames.append((column['name'], etable, ecolumn))
                return tuple(tcnames)

    @staticmethod
    @memoize(size=2)
    def check(tables: tuple[dict, ...]) -> tuple[bool, str | None]:
        """
        Check if a tuple of table dicts is well-formed

        :param tables: (tuple[dict, ...]) Tuple of table dictionaries
        :returns: (tuple[bool, str | None]) Whether all table dicts are well-formed or not and a message explaining why they are mal-formed if they are
        """
        # Loop trough tables
        for table in tables:
            # Required keys
            if not (('name' in table) and ('columns' in table)):
                return False, 'Required keys \'name\' and/or \'columns\' missing from table!'
            # Check types
            if not (isinstance(table['name'], str) and isinstance(table['columns'], tuple)):
                return False, 'Required keys \'name\' and/or \'columns\' from table have invalid types!'
            # Loop trough columns
            for column in table['columns']:
                # Check type
                if not isinstance(column, dict):
                    return False, 'One or more \'column\' values are not dictionaries!'
                # Required keys
                if not (('name' in column) and ('type' in column)):
                    return False, 'Required keys \'name\' and/or \'type\' missing from column!'
                # Check types
                if not (isinstance(column['name'], str) and isinstance(column['type'], str)):
                    return False, 'Required keys \'name\' and/or \'type\' from column have invalid types!'
                # Optional keys and key type
                if ('mods' in column):
                    if not isinstance(column['mods'], tuple):
                        return False, 'One or more \'mods\' entries are not tuples!'
                    # Loop trough mods
                    for mod in column['mods']:
                        # Check type
                        if not isinstance(mod, str):
                            return False, 'One or more \'mod\' values are not strings!'
            # Optional keys and key type
            if ('indexes' in table):
                # Check type
                if not isinstance(table['indexes'], tuple):
                    return False, 'One or more \'indexes\' entries are not tuples!'
                # Loop trough indexes
                for index in table['indexes']:
                    # Check type
                    if not isinstance(index, dict):
                        return False, 'One or more \'index\' values are not dictionaries!'
                    # Required keys
                    if not (('name' in index) and ('columns' in index)):
                        return False, 'Required keys \'name\' and/or \'columns\' missing from index!'
                    # Check types
                    if not (isinstance(index['name'], str) and isinstance(index['columns'], tuple)):
                        return False, 'Required keys \'name\' and/or \'columns\' from index have invalid types!'
                    # Optional keys and key type
                    if ('unique' in index) and not isinstance(index['unique'], bool):
                        return False, 'One or more \'unique\' entries are not booleans!'
                    # Loop trough columns
                    for column in index['columns']:
                        # Check type
                        if not isinstance(mod, str):
                            return False, 'One or more indexes \'column\' values are not strings!'
        return True, None

    @staticmethod
    @memoize(size=16)
    def _ctable(table: dict) -> str:
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
        pkeys = [f'PRIMARY KEY(']
        # Loop trough defined columns
        for column in table['columns']:
            # Column creation instruction
            query.append(f'{column['name']} {column['type']}')
            # If modifiers are specified
            for mod in column.get('mods', ()):
                # Special modifier handled differently
                if ('PRIMARY KEY' in mod):
                    pkeys.append(column['name'])
                    pkeys.append(', ')
                else:
                    query.append(f' {mod}')
            # Comma separator (gets overwritten)
            query.append(', ')
        # End of definition (overwrites last comma)
        pkeys[-1] = ')'
        query[-1] = f', {''.join(pkeys)}) STRICT;'
        return ''.join(query)

    @staticmethod
    @memoize(size=16)
    def _cindex(table: dict, index: dict) -> str:
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

@readonly(attrs={'__id', '__schema', '__path', '__uri'})
class Database:
    """
    Manages a SQL database and its schema
    """
    subscribed: set[object, ...] = set()

    def __init__(self, id: str, schema: Schema, path: Path='./', uri: bool=False) -> None:
        """
        Database object constructor

        :param id: (str) Name of the database and its file
        :param schema: (Schema) Schema instance to use for the database
        :param path: (Path) Path to save database file to, defaults to './'
        :param uri: (bool) Whether the database path is a sqlite uri, defaults to False
        :raises PathError: When the provided path is not an existing directory
        """
        # If path is not existing dir
        if not isdir(path):
            raise PathError(f'Path {path} is not an existing directory!')
        # Set attributes
        self.__id: str = id
        self.__schema: Schema = schema
        self.__path: Path = abspath(path)
        self.__uri: bool = uri
        self.__connection: sql.Connection | None = None

    def __del__(self) -> None:
        """
        Database object destructor

        :raises ConnectionError: When there is an error when closing the connection to the database file
        """
        self.close()

    def __contains__(self, tdata: tuple[str, dict[str, Any]]) -> bool:
        """
        Check if the database has specific entries in a table

        :param tdata: (tuple[str, dict[str, Any]]) The table to check on and entries to check for
        :returns: (bool) Whether the database has the entries in the table or not
        :raises ConnectionError: When trying to query the database with no open connection
        :raises QueryError: When the underlying query operation fails
        """
        # If no pkeys assume it does not contain
        if self.__schema.get_pkeys(self.__schema, tdata[0], allow=tuple(tdata[1].keys())):
            # Query number of rows with current pkeys values
            cs = self.query(f'SELECT COUNT(*) AS count FROM {tdata[0]} WHERE {self.__get_target(self, tdata[0], allow=tuple(tdata[1].keys()))};', tdata[1])
            # Get row
            row = cs.fetchone()
            # Technically impossible
            if not row:
                raise QueryError('Something has happened and we don\'t know what')
            return (row['count'] > 0) # If count > 0 it has entries
        return False

    def __str__(self) -> str:
        """
        Get a string representation of the database

        :returns: (str) String representation of the database
        """
        return f'<Database {id(self)}>' # Used for memoize

    @property
    def id(self) -> str:
        """
        Get the database id

        :returns: (str) The database id
        """
        return self.__id

    @property
    def schema(self) -> Schema:
        """
        Get the database schema

        :returns: (Schema) The database schema
        """
        return self.__schema

    @property
    def path(self) -> str:
        """
        Get the database path

        :returns: (str) The database path
        """
        return self.__path + self.__id + '.db'

    @property
    def uri(self) -> bool:
        """
        Get the database uri state

        :returns: (bool) The database uri state
        """
        return self.__uri

    @property
    def is_init(self) -> bool:
        """
        Check if the database is initialized

        The database is considered initialized if
        it has an open connection and its schema is active.

        :returns: (bool) Whether the database is initialized
        :raises ConnectionError: When schema-operation derived queries act on a db with no connection
        :raises QueryError: When schema-operation derived queries fail
        """
        return self.__connection and \
            self.__schema.is_active(self)

    @property
    def delta(self) -> int:
        """
        Get the current connection's delta

        The delta is the total number of database rows
        that have been modified, inserted, or deleted
        since the database connection was opened

        :returns: (int) The connection delta
        """
        return self.__connection.total_changes

    def init(self) -> None:
        """
        Initialize the database

        Opens the connection to the database file,
        then it drops and applies the database schema.

        :raises ConnectionError: When schema-operation derived queries act on a db with no connection
        :raises QueryError: When schema-operation derived queries fail
        """
        # Open connection
        self.open()
        # Drop and apply schema
        self.__schema.drop(self) # Erases all info in db
        self.__schema.apply(self)

    def sinit(self) -> None:
        """
        Initializes the database softly

        Opens the connection to the database file,
        then it drops and applies the database schema
        if it is not currently active on the database.

        :raises ConnectionError: When schema-operation derived queries act on a db with no connection
        :raises QueryError: When schema-operation derived queries fail
        """
        # Open connection
        self.open()
        # If schema not yet applied
        if not self.__schema.is_active(self):
            # Drop and apply schema
            self.__schema.drop(self) # Erases all info in db
            self.__schema.apply(self)

    def open(self) -> None:
        """
        Opens the connection to the database file

        If there is a currently open connection it fails silently.

        :raises ConnectionError: When there is an error when opening a connection to the database file
        """
        try:
            if not self.__connection:
                self.__connection = sql.connect(self.__id if self.__uri else f'{self.__path}/{self.__id}.db', uri=self.__uri, autocommit=False)
                self.__connection.row_factory = sql.Row # Use row objects for rows instead of tuples
        except sql.Error as e:
            raise ConnectionError(f'On DB open, {e}')

    def close(self) -> None:
        """
        Closes the connection to the database file

        If there is no currently open connection it fails silently.

        :raises ConnectionError: When there is an error when closing the connection to the database file
        """
        try:
            if self.__connection:
                # Commit before closing connection
                self.__connection.commit()
                self.__connection.close()
                self.__connection = None
        except sql.Error as e:
            raise ConnectionError(f'On DB close, {e}')

    def query(self, query: str, parameters: dict[str, Any] | Iterable=()) -> sql.Cursor | None:
        """
        Make a SQL Query on the database

        The connection to the database file must already be opened.

        :param query: (str) SQL Query string
        :param parametes: (dict[str, Any] | Iterable) Parameters to be substituted in the query string, if any
        :returns: (sql.Cursor | None) Cursor object representing query used to manage the context of a fetch operation
        :raises ConnectionError: When trying to query the database without a connection to the database file
        :raises QueryError: When there is a problem with the query and it fails
        """
        if not self.__connection:
            raise ConnectionError('On DB query, cannot query empty connection!')
        try:
            # Commits on context exit, and rollsback on error, does not close
            with self.__connection:
                if (type(parameters) == dict):
                    cursor = self.__connection.execute(query, parameters)
                else:
                    cursor = self.__connection.execute(query, (*parameters,))
            return cursor
        except sql.Error as e:
            raise QueryError(e, query, parameters)

    def store[C](self, obj: C, cdata: dict[str, Any]={}) -> None:
        """
        Store a previously subscribed object type in the database

        Object types can be subscribed using the :py:deco:`db.Database.register` decorator.
        After subscribing an object type it can be stored in the database using this method.
        Objects not stored in the database will create new rows on their tables upon storage.
        Objects already stored in the database will update their rows on their tables upon storage.
        As a consecuence it is highly advised that objects ensure the integrity of their primary key attributes.

        :param obj: (C) Object instance to store in the database
        :param cdata: (dict[str, Any]) Optional dictionary with keys as column names and values as data which overwrites object data
        :raises SubscriptionError: When the object type is not subscribed or subscribed incorrectly
        :raises ConnectionError: When trying to store on the database without a connection to the database file
        :raises QueryError: When any underlying query operation fails
        """
        # Full mapping
        fmap = {}
        # Loop trough reversed mro
        for ob in type(obj).__mro__[::-1]:
            # If object's class subscribed
            if (ob in type(self).subscribed) and getattr(ob, '__db__', None):
                # Metadata dict
                mt = ob.__db__
                # Add current map
                fmap = {**fmap, **mt['__map__']}
                # Table does not exist
                if not self.__schema.has_table(self, mt['__table__']):
                    raise SubscriptionError(f'Object {ob} subscribed to \'{mt['__table__']}\' table which {self} does not have!')
                # Get data dict
                data: dict[str, Any] = {**{str(k): getattr(obj, v, None) for k,v in mt['__map__'].items()}, **{k:v for k,v in cdata.items() if k in mt['__map__'].keys()}} # Merged as {**x, **y}
                # Check external references
                if (erefs := self.__schema.get_erefs(self.__schema, mt['__table__'])):
                    # Loop trough external references
                    for eref in erefs:
                        try:
                            # Get eref value
                            row = self.query(f'SELECT {eref[2]} FROM {eref[1]} WHERE {self.__get_target(self, eref[1], allow=tuple(fmap.keys()))};', {str(k): getattr(obj, v, None) for k,v in fmap.items()}).fetchone()
                            # Dependency not satisfied
                            if not row:
                                raise SubscriptionError(f'Object {ob} has malformed reference dependency as parent \'{eref[1]}({eref[2]})\' is uninstantiated!')
                            # Update data
                            data = {**data, **{eref[0]:row[eref[2]]}} # Merged as {**x, **y}
                        except QueryError:
                            raise SubscriptionError(f'Object {ob} has references to \'{eref[1]}({eref[2]})\' which has no related subscription!')
                # If exists row update, else insert
                if ((mt['__table__'], data) in self):
                    # Create update  query
                    self.query(
                        f'UPDATE {mt['__table__']} SET {','.join([f'{column}=:{column}' for column in data.keys()])} WHERE {self.__get_target(self, mt['__table__'], allow=tuple(data.keys()))};',
                        data
                    )
                else:
                    # Create insertion query
                    self.query(
                        f'INSERT INTO {mt['__table__']} ({','.join(data.keys())}) VALUES ({','.join(['?']*len(data))})',
                        data.values()
                    )

    def retrieve[C](self, cls: Type[C], cdata: dict[str, Any]={}) -> Iterator[C]:
        """
        Retrieve a previously subscribed object type from the database

        Object types can be subscribed using the :py:deco:`db.Database.register` decorator.
        After subscribing an object type it can be retrieved from the database using this method.

        :param cls: (Type[C]) Object type to retrieve from the database
        :param cdata: (dict[str, Any]) Optional dictionary with keys as column names and values as data to use as select constraints
        :returns: (Iterator[C]) Iterator that iterates the object type resulting instances, one for each table entry matched
        :raises SubscriptionError: When the object type is not subscribed or subscribed incorrectly
        :raises ConnectionError: When trying to store on the database without a connection to the database file
        :raises QueryError: When any underlying query operation fails
        """
        # Full mapping
        fmap = {}
        # Collected data rows and erefs per table
        table_rows: dict[str, tuple[tuple[tuple[str, str, str], ...], tuple[sql.Row, ...]]] = {}
        # Collected external rows
        table_erows: dict[str, tuple[str, ...]] = {}
        # Loop trough normal mro
        for cl in cls.__mro__:
            # If class subscribed
            if (cl in type(self).subscribed) and getattr(cl, '__db__', None):
                # Metadata dict
                mt = cl.__db__
                # Add current map
                fmap = {**fmap, **mt['__map__']}
                # Table does not exist
                if not self.__schema.has_table(self, mt['__table__']):
                    raise SubscriptionError(f'Object {cl} subscribed to \'{mt['__table__']}\' table which {self} does not have!')
                # Get table's erefs
                erefs = self.__schema.get_erefs(self.__schema, mt['__table__'])
                # Get query target
                etarget = self.__get_target(self, mt['__table__'], allow=tuple(cdata.keys()), ext=True)
                # Create and execute select statement
                cs = self.query(f'SELECT {','.join((*mt['__map__'].keys(), *{eref[0] for eref in erefs}, *(((mt['__table__'] in table_erows) and table_erows[mt['__table__']]) or ())))} FROM {mt['__table__']} \
                    {f'WHERE {etarget}' if etarget else ''};', cdata)
                # Collect row data and erefs
                table_rows[mt['__table__']] = (erefs, cs.fetchall())
                # Loop trough erefs
                for eref in erefs:
                    # Store erows
                    table_erows[eref[1]] = {*(((eref[1] in table_erows) and table_erows[eref[1]]) or ()), eref[2]}
        # Loop trough normal mro
        for cl in cls.__mro__:
            # If class subscribed
            if (cl in type(self).subscribed) and getattr(cl, '__db__', None):
                # Metadata dict
                mt = cl.__db__
                # Get erefs and rows
                erefs, rows = table_rows[mt['__table__']]
                # Recursive function to find list of eref connected rows
                def _ematch(erefs: tuple[tuple[str, str, str], ...], row: sql.Row) -> set[sql.Row, ...]:
                    # Result set
                    rset = set()
                    # Loop trough erefs
                    for eref in erefs:
                        # Loop trough erows
                        for erow in table_rows[eref[1]][1]:
                            # Matched eref with corresponding erow
                            if (row[eref[0]] == erow[eref[2]]):
                                # Union the match to rset
                                rset |= {row, erow, *_ematch(table_rows[eref[1]][0], erow)}
                    return rset
                # Loop trough rows
                for row in rows:
                    # Get row set
                    if (rset := _ematch(erefs, row)):
                        # Create new object instance
                        obj = cls.__new__(cls)
                        # Loop trough rset rows
                        for _row in rset:
                            # Loop trough row's columns
                            for column in _row.keys():
                                # If column is mapped to attr
                                if column in fmap:
                                    # Set new object instance's attribute
                                    obj.__dict__[fmap[column]] = _row[column] # Bypass __setattr__
                        # If init function defined call it
                        if callable(mt['__init__']):
                            mt['__init__'](obj)
                        # Yield object instance
                        yield obj
            break # Loop only until lowest level

    def delete[C](self, obj: C, cdata: dict[str, Any]={}) -> None:
        """
        Delete a previously subscribed object type from the database

        Object types can be subscribed using the :py:deco:`db.Database.register` decorator.
        After subscribing an object type it can be deleted from the database using this method.

        :param obj: (C) Object instance to delete from the database
        :param cdata: (dict[str, Any]) Optional dictionary with keys as column names and values as data which overwrites object data
        :raises SubscriptionError: When the object type is not subscribed or subscribed incorrectly
        :raises ConnectionError: When trying to delete from the database without a connection to the database file
        :raises QueryError: When any underlying query operation fails
        """
        # Full mapping
        fmap = {}
        # Statement cache
        sttmnts: list[tuple[str, dict[str, Any] | Iterable]] = []
        # Loop trough reversed mro
        for ob in type(obj).__mro__[::-1]:
            # If object's class subscribed
            if (ob in type(self).subscribed) and getattr(ob, '__db__', None):
                # Metadata dict
                mt = ob.__db__
                # Add current map
                fmap = {**fmap, **mt['__map__']}
                # Table does not exist
                if not self.__schema.has_table(self, mt['__table__']):
                    raise SubscriptionError(f'Object {ob} subscribed to \'{mt['__table__']}\' table which {self} does not have!')
                # Get data dict
                data: dict[str, Any] = {**{str(k): getattr(obj, v, None) for k,v in mt['__map__'].items()}, **{k:v for k,v in cdata.items() if k in mt['__map__'].keys()}} # Merged as {**x, **y}
                # Check external references
                if (erefs := self.__schema.get_erefs(self.__schema, mt['__table__'])):
                    # Loop trough external references
                    for eref in erefs:
                        try:
                            # Get eref value
                            row = self.query(f'SELECT {eref[2]} FROM {eref[1]} WHERE {self.__get_target(self, eref[1], allow=tuple(fmap.keys()))};', {str(k): getattr(obj, v, None) for k,v in fmap.items()}).fetchone()
                            # Dependency not satisfied
                            if not row:
                                raise SubscriptionError(f'Object {ob} has malformed reference dependency as parent \'{eref[1]}({eref[2]})\' is uninstantiated!')
                            # Update data
                            data = {**data, **{eref[0]:row[eref[2]]}} # Merged as {**x, **y}
                        except QueryError:
                            raise SubscriptionError(f'Object {ob} has references to \'{eref[1]}({eref[2]})\' which has no related subscription!')
                # Store statement in cache
                sttmnts.append((f'DELETE FROM {mt['__table__']} WHERE {self.__get_target(self, mt['__table__'], allow=tuple(data.keys()))};', data))
        # Loop trough statements in reverse
        for sttmnt in sttmnts[::-1]:
            # Create and execute delete statement
            self.query(sttmnt[0], sttmnt[1])

    def dump(self, path: Path) -> None:
        """
        Create a SQL dump of the database

        :param path: (Path) Path to dump the database to
        :raises ConnectionError: When the database has no open connection or there is an error when connecting to the dump target
        """
        if not self.__connection:
            raise ConnectionError('On DB dump, cannot dump with empty connection!')
        try:
            # Open file to dump to
            with open(path + '.sql', 'w') as file:
                # Loop trough lines of iterdump
                for line in self.__connection.iterdump():
                    file.write('%s\n' % line) # Write each line
        except OSError as e:
            raise ConnectionError(f'On DB dump, problem with dump target: {e}')

    def backup(self, path: Path, uri: bool=False, *args, **kwargs) -> None:
        """
        Create a backup of the database

        :param path: (Path) Path to backup the database to
        :param uri: (bool) Whether the backup path is a sqlite uri, defaults to False
        :param pages: (int) Number of pages to copy at a time, if equal to or less than 0, the entire database is copied in a single step, defaults to -1
        :param progress: (Callable[[int, int, int], None]) Optional callable invoked for every backup iteration with args: status of the last iteration, remaining pages to be backup, total pages
        :param sleep: (float) Number of seconds to sleep between successive attempts to back up remaining pages, defaults to 0.250
        :raises ConnectionError: When the database has no open connection or there is an error when connecting to the backup target
        """
        if not self.__connection:
            raise ConnectionError('On DB backup, cannot backup with empty connection!')
        try:
            # Open target connection
            target = sql.connect(path, uri=uri, autocommit=False)
            # Commits on context exit, and rollsback on error, does not close
            with target:
                self.__connection.backup(target, *args, **kwargs)
            # Close after backup
            target.close()
        except sql.Error as e:
            raise ConnectionError(f'On DB backup, {e}')

    @memoize
    def __get_target(self, table: str, allow: tuple[str, ...]=(), ignore: tuple[str, ...]=(), ext: bool=False) -> str:
        """
        Get placeholder condition expression to target any specific row of a table by its primary keys

        :param table: (str) Table to get expresion for
        :param allow: (tuple[str, ...]) Tuple of columns to allow
        :param ignore: (tuple[str, ...]) Tuple of columns to ignore
        :param ext: (bool) Whether the target should include no-pkey columns
        :returns: (str) Placeholder condition expression for the table
        """
        if ext:
            return ' AND '.join([f'{nkey}=:{nkey}' for nkey in (self.__schema.get_nkeys(self.__schema, table, allow, ignore) or ())])
        else:
            return ' AND '.join([f'{pkey}=:{pkey}' for pkey in (self.__schema.get_pkeys(self.__schema, table, allow, ignore) or ())])

    @classmethod
    def from_schema(cls, id: str, *tables: dict) -> Self:
        """
        Database object alternative constructor

        :param id: (str) Name of the database and its file
        :param schema: (*tables) Table dicts that define the database schema
        :returns: (Database) The new object instance
        """
        return cls(id, Schema(*tables))

    @dec_wparams
    @staticmethod
    def register[C](cls: Type[C], table: str, map: dict[str, str], init: Callable[[C], None] | None=None, db: Self | None=None) -> Type[C]:
        """
        Register a class for database storage and retrieval

        :param cls: (C) Class object to register
        :param table: (str) Database table to register it to
        :param map: (dict[str, str]) Mapping of table columns and instance attributes
        :param init: (Callable[[C], None]) Optional initialization function for when retrieving instances, gets passed the instance with the data as a parameter
        :param db: (Self) Optional database instance to update instances to automatically on attribute set
        :returns: (C) The registered class object
        """
        # Register class object
        Database.subscribed.add(cls)
        # Store database metadata
        cls.__db__ = {
            '__table__': table,
            '__map__': map,
            '__init__': init,
            '__db__': db
        }
        # If passed db
        if db:
            # Define __init__ magic method
            def _init[**P](init: Callable[P, None]) -> None:
                """
                Set the corresponding flags on init call

                :param args: (P.args) Positional arguments to init call
                :param kwargs: (P.kwargs) Keyword arguments to init call
                """
                def _init_wp(self, *args: P.args, **kwargs: P.kwargs) -> None:
                    # If already in init recursion
                    if getattr(self, '__in_init__', False):
                        # Simply call next piece
                        init(self, *args, **kwargs)
                    else:
                        # Start init recursion
                        self.__dict__['__in_init__'] = True
                        # Call init recursion
                        init(self, *args, **kwargs)
                        # Stop init recursion
                        if '__in_init__' in self.__dict__:
                            del self.__dict__['__in_init__']
                # Return wrapper
                return _init_wp

            # Define __setattr__ magic method
            def _setattr(self, key: str, value: Any) -> None:
                """
                Set the corresponding value for a attribute key

                :param key: (str) The key to set the value for
                :param value: (Any) The value to set the attribute to
                """
                # Call parent method to handle call
                super(cls, self).__setattr__(key, value)
                # Check if in init
                if not getattr(self, '__in_init__', False):
                    # If key to set is registered
                    if key in map.values():
                        # Update object in database
                        db.store(self)
            # Set __init__ magic method
            cls.__init__ = _init(cls.__init__)
            # Set __setattr__ magic method
            cls.__setattr__ = _setattr
        # Return class
        return cls

class Singleton[C: object](type):
    """
    Singleton metaclass

    Enforces the singleton pattern on a class.
    """
    __instances: dict[Self, C] = {}

    def __call__[**P](cls, *args: P.args, **kwargs: P.kwargs) -> C:
        """
        Construct a class object following the singleton pattern

        Constructs an object or returns one if it was already made before.
        """
        if not (cls in cls.__instances):
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]

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
                        {'name': 'phone', 'type': 'TEXT'},
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
                        {'name': 'fecha', 'type': 'TEXT', 'mods': ('NOT NULL',)},
                        {'name': 'description', 'type': 'TEXT'},
                        {'name': 'image', 'type': 'BLOB'},
                    ),
                    'indexes': (
                        {'name': 'posts_user', 'columns': ('user',)},
                    )
                },
                {
                    'name': 'offer',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES posts(id)')},
                        {'name': 'price', 'type': 'INTEGER', 'mods': ('NOT NULL',)},
                        {'name': 'contractor', 'type': 'INTEGER', 'mods': ('REFERENCES consumers(id)',)},
                    )
                },
                {
                    'name': 'demand',
                    'columns': (
                        {'name': 'id', 'type': 'INTEGER', 'mods': ('PRIMARY KEY', 'REFERENCES posts(id)')},
                        {'name': 'urgency', 'type': 'INTEGER'},
                        {'name': 'contractor', 'type': 'INTEGER', 'mods': ('REFERENCES freelancers(id)',)},
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

def main():

    @readonly(attrs={'__name'})
    @Database.gregister(
        table='freelancers'
    )
    class Freelancer(User):
        def __init__(self, name:str, pwd: str):
            super().__init__(name, pwd)
            self.nombre_freelancer = nombre_freelancer

    db = Database('Sixerrr', schema)
    u1 = User('pepe', '1234')


    db.store(u1)


    for user in db.retrieve(User):
        User.usuarios[user.username] = user
    return

    db = SixerrDB(schema)
    if not db.init():
        print('Something went wrong')
    print(db.is_init)
    #db.schema.drop(db)
    print(db.is_init)









if __name__ == '__main__':
    main()
