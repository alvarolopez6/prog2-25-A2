import sqlite3 as sql
from os import PathLike
from os.path import abspath, isdir
from tkinter.constants import SEPARATOR
from typing import Self, Type, Callable, Iterator

from utils.decorators import dec_wparams, readonly, memoize
from .schema import Schema
from .exceptions import *
import builtins

class Adapters:
    SEPARATOR = '¨'
    SUBSEPARATOR = '¬'

    @staticmethod
    def from_tuple(o: list) -> str:
        return Adapters.from_list(o)

    @staticmethod
    def from_list(o: list) -> str:
        ss = []
        for item in o:
            ss.append(type(item).__name__ + Adapters.SUBSEPARATOR + str(item))
        return SEPARATOR.join(ss)

    @staticmethod
    def to_list(s: bytes) -> list:
        o = []
        oo = s.decode().split(SEPARATOR)
        for item in oo:
            t, v = item.split(Adapters.SUBSEPARATOR)
            try:
                o.append(getattr(builtins, t)(v))
            except (AttributeError, ValueError, TypeError) as e:
                raise ValueError(f"Cannot create instance of type '{t}' with value '{v}': {e}")
        return o

    @staticmethod
    def to_tuple(s: bytes) -> tuple:
        return tuple(Adapters.to_list(s))

# Register the adapter and converter
sql.register_adapter(list, Adapters.from_list)
sql.register_converter("LIST", Adapters.to_tuple)

sql.register_adapter(tuple, Adapters.from_tuple)
sql.register_converter("TUPLE", Adapters.to_tuple)

type Path = str | bytes | PathLike[str] | PathLike[bytes]

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
            #print('\n')
            #print(f'SELECT COUNT(*) AS count FROM {tdata[0]} WHERE {self.__get_target(self, tdata[0], allow=tuple(tdata[1].keys()))};')
            #print(tdata, '-->', (row['count'] > 0))
            return (row['count'] > 0) # If count > 0 it has entries
        #print(tdata, '-->', False, 'Ex')
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
                self.__connection = sql.connect(self.__id if self.__uri else f'{self.__path}/{self.__id}.db', uri=self.__uri, detect_types=sql.PARSE_DECLTYPES, autocommit=False, check_same_thread=False)
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
        :param parameters: (dict[str, Any] | Iterable) Parameters to be substituted in the query string, if any
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
                        except QueryError as e:
                            print(e, '\n\n')
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
        # If object's class subscribed
        if (type(obj) in type(self).subscribed) and getattr(type(obj), '__db__', None):
            # Metadata dict
            mt = type(obj).__db__
            # If store function defined call it
            if callable(mt['__store__']):
                mt['__store__'](obj, self)

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
                etarget = self.__get_target(self, mt['__table__'], allow=(cdata.keys(), ''), ext=True)
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
                        for cl in cls.__mro__[::-1]:
                            # If class subscribed
                            if (cl in type(self).subscribed) and getattr(cl, '__db__', None):
                                init = cl.__db__['__init__']
                                # If init function defined call it
                                if callable(init):
                                    init(obj, self)
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
    def register[C](cls: Type[C], table: str, map: dict[str, str], init: Callable[[C, Self], None] | None=None, store: Callable[[C, Self], None] | None=None, db: Self | None=None) -> Type[C]:
        """
        Register a class for database storage and retrieval

        :param cls: (C) Class object to register
        :param table: (str) Database table to register it to
        :param map: (dict[str, str]) Mapping of table columns and instance attributes
        :param init: (Callable[[C, Self], None]) Optional initialization function for when retrieving instances, gets passed the instance with the data and the database as parameters
        :param store: (Callable[[C, Self], None]) Optional storage function for when storing instances, gets passed the instance with the data and the database as parameters
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
            '__store__': store,
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
                        # Update object in database
                        db.store(self)
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