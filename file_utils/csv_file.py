"""
Module csv_file.py

Defines class 'CSVFile(File)' for reading and writing CSV files.

Author: Ismael Escribano
Creation Date: 29-03-2025
"""
import csv

from . import Path
from .file import File

class CSVFile(File):
    """
    Class for handling Read and Write operations on CSV files.

    Attributes
    ----------
    path: Path | str
        System path to the file
    data: list[list[str]]
        List of lists that contains all CSV data (rows)
    headers: list[str]
        List that contains all headers (columns)

    Methods
    -------
    write_headers(fieldnames: list[str]) -> None
        Writes the headers into a CSV file
    write(content: list[str]) -> None
        Writes a single row into a CSV file (headers must exist)
    read -> None
        Reads the CSV file if it exists
    __str__() -> str
        Returns the string representation of the CSV file.
    """
    def __init__(self, path: Path | str) -> None:
        """
        Initializes a CSVFile instance

        Parameters
        ----------
        path : Path | str
            System path to file, it must end with '.csv'
        """
        super().__init__(path)
        if self.path.extension != '.csv':
            self.path.change_extension('.csv')
        self.data: list[list[str]] = []
        self.headers: list[str] = []

    def write_headers(self, fieldnames: list[str]) -> None:
        """
        Writes the headers into a CSV file

        Parameters
        ----------
        fieldnames: list[str]
            List that contains all headers (columns) to be written
        """
        with open(str(self.path), newline='', mode='w') as csv_file:
            writer  = csv.DictWriter(csv_file, fieldnames=fieldnames)
            self.headers = fieldnames
            writer.writeheader()
        return None

    def write(self, content: list[str]) -> None:
        """
        Writes a single row into a CSV file

        Parameters
        ----------
        content: list[str]
            List that contains a row data to be written (headers must exist)
        """
        if not self.headers:
            raise NotImplementedError("Headers must exist before writing.")
        mode = 'a' if self.path.exists else 'w'

        with open(str(self.path), mode=mode, newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers)
            row: dict = {}
            for i in range(len(content)):
                try:
                    row[self.headers[i]] = content[i]
                except IndexError:
                    row[self.headers[i]] = None
            writer.writerow(row)
        return None

    @property
    def read(self) -> None:
        """
        Reads the CSV file if it exists, it appends CSV's data into 'self.data'
        """
        if self.path.exists:
            with open(str(self.path), mode='r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                cont = 0
                for row in csv_reader:
                    if cont == 0:
                        self.headers = row
                        cont += 1
                    else:
                        self.data.append(row)
        return None

    def __str__(self) -> str:
        """
        Returns CSV file system path and data (headers and rows) as string

        Returns
        -------
        str
            String representation of the CSV file.
        """
        output = f'File path: {self.path.absolute}\nData:\n{self.headers}'
        for i in self.data:
            output += f'\n{i}'
        return output