"""
Module file.py

Defines basic class 'File' for handling files

Author: Ismael Escribano
Creation Date: 29-03-2025
"""

from typing import Sequence, Mapping
from abc import ABC, abstractmethod
from file_utils import Path

class File:
    """
    Abstract class for handling file operation

    Attributes
    ----------
    path: Path
        System Path to the file

    Methods
    -------
    is_empty -> bool
        Checks if the file is empty
    clear() -> None
        Clears the file's data
    delete() -> None
        Deletes the file
    __str__() -> str
        Returns the string representation of the file
    """

    def __init__(self, path: Path | str) -> None:
        """
        Initializes a File instance

        Parameters
        ----------
        path : Path | str
            System path to file, if it is str, it is converted into Path
        """
        self.path = Path(path) if type(path) == str else path

    @property
    def is_empty(self) -> bool:
        """
        Checks if the file is empty (file must exist)

        Returns
        -------
        bool
            True if the file is empty, False otherwise
        """
        return self.path.exists and self.path.path.stat().st_size == 0

    def clear(self) -> None:
        """
        Clears the file's data
        """
        with open(str(self.path), mode='w', encoding='utf-8'):
            pass

    def delete(self) -> None:
        """
        Deletes the file if it exists.
        """
        if self.path.exists:
            self.path.path.unlink(missing_ok=True)

    def __str__(self) -> str:
        """
        Returns file system path as string

        Returns
        -------
        str
            String representation of file's system path.
        """
        return f'System Path: {self.path}'


class Exportable(ABC, File):
    """
    Abstract class for indicating an exportable file (can be written)

    Methods
    -------
    write(content: str | Sequence | Mapping) -> None
        Writes content into the file (Must be implemented by subclasses)
    """
    @abstractmethod
    def write(self, content: str | Sequence | Mapping) -> None:
        """
        Writes content into the file (Must be implemented by subclasses)

        Parameters
        ----------
        content : str | Sequence | Mapping (depends on subclass)
             Content to be written into the file
        """
        pass

class Importable(ABC, File):
    """
    Abstract class for indicating an importable file (can be read)

    Methods
    read() -> None
        Reads the file's content (Must be implemented by subclasses)
    """
    @abstractmethod
    def read(self) -> None:
        """
        Reads the file's content (Must be implemented by subclasses)

        NOTE: Subclasses must have 'data' attribute, otherwise this method should return a Sequence or str
        """
        pass