# <===============================================>

#     ██████╗███████╗██╗   ██╗  ██████╗ ██╗   ██╗
#    ██╔════╝██╔════╝██║   ██║  ██╔══██╗╚██╗ ██╔╝
#    ██║     ███████╗██║   ██║  ██████╔╝ ╚████╔╝ 
#    ██║     ╚════██║╚██╗ ██╔╝  ██╔═══╝   ╚██╔╝  
#    ╚██████╗███████║ ╚████╔╝██╗██║        ██║   
#     ╚═════╝╚══════╝  ╚═══╝ ╚═╝╚═╝        ╚═╝   
                                            
# <===============================================>
#          Module for managing CSV files
# <===============================================>
#          @Author: Stefano Bia Carrasco
# <===============================================>
#  IMPORTS
# <===============================================>
#  Math imports
# <===============================================>
from math import inf
# <===============================================>
#  Operating System imports
# <===============================================>
import os.path as op
from os import PathLike
# <===============================================>
#  Typing imports
# <===============================================>
from typing import Self
# <===============================================>
#  CLASSES
# <===============================================>
#  Path class
# <===============================================>
class Path(PathLike):
    """
    Class representing a filesystem path
    """

    def __init__(self, path: str, sep: str='/') -> None:
        """
        Initializes a Path instance

        Parameters:
        path (str): Path, as a string, to refer to.
        sep (str): Separator used between path nodes. Defaults to '/'.
        """
        self.pointer: list[str, ...] = type(self).get_pointer(path, sep)
        self.sep: str = sep

    def __str__(self) -> str:
        """
        Returns the string representation of the path
        """
        return self.sep.join(self.pointer)

    def __fspath__(self) -> str:
        """
        Returns the filesystem path representation of the object
        """
        return str(self)

    def __eq__(self, other: Self) -> bool:
        """
        Whether two Path objects point to the same file or directory
        """
        return op.samefile(self, other)

    @property
    def exists(self) -> bool:
        """
        Whether the path refers to an existing path
        """
        return op.exists(self)

    @property
    def is_file(self) -> bool:
        """
        Whether the path refers to an existing file
        """
        return op.isfile(self)

    @property
    def is_dir(self) -> bool:
        """
        Whether the path refers to an existing directory
        """
        return op.isdir(self)

    @property
    def is_mount(self) -> bool:
        """
        Whether the path refers to an existing mount point
        """
        return op.ismount(self)

    @property
    def is_symlink(self) -> bool:
        """
        Whether the path refers to an existing symbolic link
        """
        return op.islink(self)

    @staticmethod
    def get_pointer(path: str, sep: str) -> list[str, ...]:
        """
        Gets the pointer structure of a path

        Parameters:
        path (str): Path, as a string, to point to.
        sep (str): Separator used between path nodes. Defaults to '/'.

        Returns:
        list[str, ...]: Pointer structure to path
        """
        # Expands ~/ if required
        path = op.abspath(op.expanduser(path))
        # Returns pointer list of path
        return path.split(sep)
# <===============================================>
#  File class
# <===============================================>
class File:
    """
    Class representing a filesystem text file
    """

    def __init__(self, path: str, encoding: str='utf-8') -> None:
        """
        Initializes a File instance

        Parameters:
        path (str): Path, as a string, that points to the file.
        encoding (str): Encoding to use when reading and writing to the file. Defaults to 'utf-8'.
        """
        self.path: Path = Path(path)
        self.encoding: str = encoding
        self.data: list[str, ...] = []

    @property
    def lines(self, start: int=0, length: int=inf) -> str:
        """
        Generator function to iterate through the file's cached lines

        Parameters:
        start (int): Start offset line to start iteration from.
        length (int): Number of lines to iterate through. Defaults to 'infinity'.

        Returns:
        str: Current line read as a string.
        """
        count = start
        while (count < (start + length)) and (count < len(self.data)):
            yield self.data[count]
            count += 1

    @property
    def clines(self, start: int=0, length: int=inf) -> str:
        """
        Generator function to iterate through the file's current lines

        Parameters:
        start (int): Start offset line to start iteration from.
        length (int): Number of lines to iterate through. Defaults to 'infinity'.

        Returns:
        str: Current line read as a string.
        """
        self.load()
        return self.lines

    def load(self) -> bool:
        """
        Loads the file's contents, as lines, to cache

        Returns:
        bool: Whether the operation succeded.
        """
        try:
            with open(self.path, 'tr', encoding=self.encoding) as file:
                self.data = file.readlines()
            return True
        except OSError:
            return False

    def flush(self) -> bool:
        """
        Flushes the cached contents, as lines, to the file

        Returns:
        bool: Whether the operation succeded.
        """
        try:
            with open(self.path, 'tw', encoding=self.encoding) as file:
                file.writelines(self.data)
            return True
        except OSError:
            return False

    def read(self, load: bool=True) -> list[str, ...]:
        """
        Reads from the file's cached contents

        Parameters:
        load (bool): Whether to load the file's contents from disk before reading from the cache. Default is True.

        Returns:
        list[str, ...]: List of strings where each string is a line of the file.
        """
        if load:
            self.load()
        return self.data

    def write(self, data: list[str, ...], flush: bool=True) -> None:
        """
        Writes to the file's cached contents

        Parameters:
        data (list[str, ...]): List of strings where each string is a line of the file.
        flush (bool): Whether to flush the file's cached contents to disk after writing to the cache. Default is True.
        """
        self.data = data
        if flush:
            self.flush()
# <===============================================>
#  CSVFile class
# <===============================================>
class CSVFile(File):
    """
    Class representing a filesystem csv file
    """

    def __init__(self, path: str, sep: str, encoding: str='utf-8') -> None:
        """
        Initializes a CSVFile instance

        Parameters:
        path (str): Path, as a string, that points to the file.
        sep (str): Separator, as a string, to use between comma-separated values.
        encoding (str): Encoding to use when reading and writing to the file. Defaults to 'utf-8'.
        """
        super().__init__(path, encoding)
        self.sep: str = sep

    @property
    def lines(self, start: int=0, length: int=inf) -> list[str]:
        """
        Generator function to iterate through the file's cached lines

        Parameters:
        start (int): Start offset line to start iteration from.
        length (int): Number of lines to iterate through. Defaults to 'infinity'.

        Returns:
        str: Current line read as a string.
        """
        return super().lines

    @property
    def clines(self, start: int=0, length: int=inf) -> list[str]:
        """
        Generator function to iterate through the file's current lines

        Parameters:
        start (int): Start offset line to start iteration from.
        length (int): Number of lines to iterate through. Defaults to 'infinity'.

        Returns:
        str: Current line read as a string.
        """     
        self.load()
        return super().lines

    def load(self) -> bool:
        """
        Loads the file's contents, as lines, to cache

        Returns:
        bool: Whether the operation succeded.
        """
        try:
            with open(self.path, 'tr', encoding=self.encoding) as file:
                self.data = []
                for line in file.readlines():
                    self.data.append(line.strip('\n').split(self.sep))
            return True
        except OSError:
            return False

    def flush(self) -> bool:
        """
        Flushes the cached contents, as lines, to the file

        Returns:
        bool: Whether the operation succeded.
        """
        try:
            with open(self.path, 'tw', encoding=self.encoding) as file:
                for line in self.data:
                    file.write(self.sep.join(line) + '\n')
            return True
        except OSError:
            return False

    def read(self, load: bool=True) -> list[list[str], ...]:
        """
        Reads from the file's cached contents

        Parameters:
        load (bool): Whether to load the file's contents from disk before reading from the cache. Default is True.

        Returns:
        list[list[str], ...]: List of lists of strings where each string is a comma-separated value and each list a line of the file.
        """
        if load:
            self.load()
        return self.data

    def write(self, data: list[list[str], ...], flush: bool=True) -> None:
        """
        Writes to the file's cached contents

        Parameters:
        data (list[list[str], ...]): List of lists of strings where each string is a comma-separated value and each list a line of the file.
        flush (bool): Whether to flush the file's cached contents to disk after writing to the cache. Default is True.
        """
        self.data = data
        if flush:
            self.flush()
# <===============================================>
#  SCRIPT EXECUTION
# <===============================================>
# If executing as a script
# <===============================================>
if (__name__ == '__main__'):
    pass
# <===============================================>