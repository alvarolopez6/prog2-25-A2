"""
Module csv_file.py

Defines class 'CSVFile(File)' for reading and writing CSV files.

Author: Ismael Escribano
Creation Date: 29-03-2025
"""
import csv
from itertools import zip_longest
from collections.abc import Sequence
from typing import Self

from file_utils import Path, Exportable, Importable


class NoHeadersFound(Exception):
    """
    Exception raised when headers are not define when writing data to a CSV file.
    """
    def __str__(self) -> str:
        return 'Headers are not defined in CSV file. Use write_headers() to define them.'


class NotEnoughColumns(Exception):
    """
    Exception raised when there is more data than headers when writing to a CSV file
    """
    def __init__(self, num_data: int, num_col: int, *args) -> None:
        super().__init__(*args)
        self.num_data = num_data
        self.num_col = num_col

    def __str__(self) -> str:
        return f'Introduced {self.num_data} elements but CSV File has {self.num_col} columns'


class CSVFile(Exportable, Importable):
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
    write_headers(fieldnames: Sequence[str]) -> None
        Writes the headers into a CSV file
    write(content: Sequence[str]) -> None
        Writes a single row into a CSV file (headers must exist)
    write_rows(rows: Sequence[Sequence[str]]) -> None
        Writes multiple rows into a CSV file (headers must exist)
    read() -> bool
        Reads the CSV file if it exists
    clear() -> None
        Clears all the CSV file data, also resets 'data' and 'headers' attributes
    __str__() -> str
        Returns the string representation of the CSV file.
    from_dict(path: Path | str, data: dict[str, Sequence[str]]) -> Self:
        Creates a CSVFile instance from a dictionary and writes data on it
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

    def write_headers(self, fieldnames: Sequence[str]) -> None:
        """
        Writes the headers into a CSV file

        Parameters
        ----------
        fieldnames: Sequence[str]
            List or tuple that contains all headers (columns) to be written
        """
        with open(str(self.path), newline='', mode='w') as csv_file:
            writer  = csv.DictWriter(csv_file, fieldnames=fieldnames)
            self.headers = fieldnames
            writer.writeheader()

    def write(self, content: Sequence[str]) -> None:
        """
        Writes a single row into a CSV file

        Parameters
        ----------
        content: Sequence[str]
            List or tuple that contains a row data to be written (headers must exist)
        """
        if not self.headers:
            raise NoHeadersFound

        if len(content) > len(self.headers):
            raise NotEnoughColumns(len(content), len(self.headers))

        with open(str(self.path), mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers)
            row: dict = {}
            for i in range(len(content)):
                try:
                    row[self.headers[i]] = content[i]
                except IndexError:
                    row[self.headers[i]] = None
            writer.writerow(row)

    def write_rows(self, rows: Sequence[Sequence[str]]) -> None:
        """
        Writes multiple rows into the CSV file

        Parameters
        ----------
        rows: Sequence[Sequence[str]]
            List or tuple that contains all rows to be written (headers must exist)
        """
        if not self.headers:
            raise NoHeadersFound
        with open(str(self.path), mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.headers)
            for row in rows:
                if len(row) > len(self.headers):
                    raise NotEnoughColumns(len(row), len(self.headers))
                row_dict: dict = {}
                for i in range(len(row)):
                    try:
                        row_dict[self.headers[i]] = row[i]
                    except IndexError:
                        row_dict[self.headers[i]] = None
                writer.writerow(row_dict)

    def read(self) -> bool:
        """
        Reads the CSV file if it exists, it appends CSV's data into 'self.data'

        Returns
        -------
        bool
            Returns True if the CSV file exists, False otherwise
        """
        self.data = []
        if self.path.exists:
            with open(str(self.path), mode='r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                cont = 0
                for row in csv_reader:
                    if cont == 0:
                        self.headers = row
                        cont += 1
                    else:
                        self.data = row
                else:
                    return True
        return False

    def clear(self) -> None:
        """
        Clears all CSV file data, also resets 'self.data' and 'self.headers'
        """
        super().clear()
        self.headers = []
        self.data = []

    @classmethod
    def from_dict(cls, path: Path | str, data: dict[str, Sequence[str]]) -> Self:
        """
        Creates a CSVFile instance from a dictionary and writes data on it

        Parameters
        ----------
        path: Path | str
            System path to file, it must end with '.csv'
        data: dict[str, Sequence[str]]
            Dictionary that contains all CSV data, keys are headers and values are all rows data for that header

        Returns
        -------
        CSVFile instance
        """
        headers: list[str] = list(data.keys())
        rows: list[Sequence[str]] = list(list(zip_longest(*data.values(), fillvalue=None)))

        csv_file = cls(path)
        csv_file.write_headers(headers)
        csv_file.write_rows(rows)
        return csv_file

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