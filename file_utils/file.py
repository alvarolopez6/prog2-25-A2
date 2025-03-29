"""
Module file.py

Defines basic class 'File' for handling files

Author: Ismael Escribano
Creation Date: 29-03-2025
"""

from abc import ABC, abstractmethod
from file_utils import Path

class File(ABC):
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
    delete() -> None
        Deletes the file
    read() -> str
        Reads the file's content (Must be implemented by subclasses)
    write(content: str) -> None
        Writes content into the file (Must be implemented by subclasses)
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

    def is_empty(self) -> bool:
        """
        Checks if the file is empty (file must exist)

        Returns
        -------
        bool
            True if the file is empty, False otherwise
        """
        return self.path.exists and self.path.path.stat().st_size == 0

    def delete(self, erase_self: bool = False) -> None:
        """
        Deletes the file if it exists.
        It can also delete the instance

        Parameters
        ----------
        erase_self: bool
            Deletes the self instance if True. Default is False
        """
        if self.path.exists:
            self.path.path.unlink(missing_ok=True)
        if erase_self:
            del self

    @abstractmethod
    def read(self) -> str | list[str]:
        """
        Reads the file's content (Must be implemented by subclasses)

        Returns
        -------
        str | list[str]
            String or list of strings that represent the file's content
        """
        pass

    @abstractmethod
    def write(self, content: str) -> None:
        """
        Writes content into the file (Must be implemented by subclasses)

        Parameters
        ----------
        content : str
            Content to be written into the file
        """
        pass