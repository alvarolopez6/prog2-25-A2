from typing import Any, Iterable

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