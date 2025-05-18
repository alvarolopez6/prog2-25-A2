from decorators import readonly, memoize

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
