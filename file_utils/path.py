"""
Module path.py

Defines basic class 'Path' for handling system paths

Author: Ismael Escribano
Creation Date: 29-03-2025
"""
from pathlib import Path as pl
from typing import Self


class Path:
    """
    Class for handling system paths

    Attributes
    ----------
    path: str
        String with a file or directory path

    Methods
    -------
    is_absolute() -> bool
        Verifies if the path is an absolute path
    absolute() -> str
         Returns a string representation of an absolute path of the path.
    exists() -> bool
        Verifies if the path exists
    is_file() -> bool
        Verifies if the path refers to a file
    extension() -> str or None
        Extracts the extension of the path if it is a file
    __add__(other: Path) -> Path
        Returns a new Path instance joining both paths
    """

    def __init__(self, path: str) -> None:
        """
        Initializes a Path instance.

        Parameters
        ----------
        path: str
            String with a file path
        """
        self.path = pl(path)


    def __str__(self) -> str:
        """
        Returns a string representation of a Path instance.

        Returns
        -------
        str
            String representation of a Path instance.
        """
        return str(self.path)

    def __repr__(self) -> str:
        """
        Returns a more repr representation of a Path instance.

        Returns
        -------
        str
            String repr representation of a Path instance.
        """
        return f"Path({self.path})"

    @property
    def is_absolute(self) -> bool:
        """
        Verifies if the path is an absolute path.

        Returns
        -------
        bool
            True if the path is an absolute path, False otherwise.
        """
        return self.path.is_absolute()

    @property
    def absolute(self) -> str:
        """
        Returns a string representation of an absolute path of the path.

        Returns
        -------
        str
            String representation of an absolute path of the path.
        """
        return str(self.path.resolve())

    @property
    def exists(self) -> bool:
        """
        Verifies if the path exists

        Returns
        -------
        bool
            True if the path exists, False otherwise.
        """
        return self.path.exists()

    @property
    def is_file(self) -> bool:
        """
        Verifies if the paths refers to a file

        Returns
        -------
        bool
            True if the path refers to a file, False otherwise.
        """
        return self.path.is_file()

    @property
    def extension(self) -> str | None:
        """
        Returns the extension of the path if it is a file, otherwise, returns None.

        Returns
        -------
        str | None
            Extension of the path if it is a file, otherwise, returns None.
        """
        if self.is_file:
            return self.path.suffix
        return None

    def __add__(self, other: Self) -> Self:
        """
        Returns a new Path instance joining both paths

        Parameters
        ----------
        other: Path
            Path to be added.

        Returns
        -------
        Path
            New Path instance with both paths joined.
        """
        if isinstance(other, Path):
            return Path(str(self.path / other.path))
        return NotImplemented