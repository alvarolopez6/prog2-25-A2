"""
Module csv_file.py

Defines class 'CSVFile(File)' for reading and writing CSV files.

Author: Ismael Escribano
Creation Date: 29-03-2025
"""
import csv

from .file import File

class CSVFile(File):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.data: list[list[str]] = []
        self.headers: list[str] = []
        # TODO: Comprobar que la ruta acaba en un archivo .csv, en caso contrario, hacerlo

    def write_headers(self, fieldnames: list[str]) -> None:
        with open(str(self.path), mode='w') as csv_file:
            writer  = csv.DictWriter(csv_file, fieldnames=fieldnames)
            self.headers = fieldnames
            writer.writeheader()

    def write(self, content: list[str]) -> None:
        if self.path.exists:
            mode = 'a'
        else:
            mode = 'w'
        if len(self.headers) > 0:
            with open(str(self.path), mode=mode) as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.headers)
                writer.writerow({'Nombre': content[0], 'Contraseña': content[1]})
        else:
            raise NotImplemented

    def read(self) -> None:
        self.data = []
        with open(str(self.path), mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            cont = 0
            for row in csv_reader:
                if cont == 0:
                    cont += 1
                else:
                    self.data.append(row)
