"""
Module xml_file.py

Defines class 'XMLFile(File)' for writing XML files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from file_utils import Path, Exportable, Importable

class XMLFile(Exportable, Importable):
    def read(self) -> None:
        pass

    def write(self, content: str) -> None:
        pass