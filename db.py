import sqlite3 as sql
from os.path import abspath, isdir
from typing import Self, Any, Type, Iterable, Iterator, Callable


from exceptions import *

type Path = str | bytes | os.PathLike[str] | PathLike[bytes]

