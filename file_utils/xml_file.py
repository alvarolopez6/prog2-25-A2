"""
Module xml_file.py

Defines class 'XMLFile(Exportable, Importable)' for writing XML files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from typing import Any
from file_utils import Path, Exportable, Importable
import xml.etree.ElementTree as ET
from demand import Demand
from offer import Offer

type_to_str = {
    int: 'int',
    float: 'float',
    bool: 'bool',
    dict: 'dict',
    list: 'list',
    tuple: 'tuple',
    set: 'set',
}

str_to_type = {
    'int': int,
    'float': float,
    'bool': bool,
    'dict': dict,
    'list': list,
    'tuple': tuple,
    'set': set,
}

# TODO: Hay que hacer métodos en las clases de post y user para convertir los atributos en elementos XML


class NoRootFound(Exception):
    """
    Exception raised when trying to write a XML file without root.
    """
    def __str__(self) -> str:
        return f'There is no Root created, use "XMLFile.gen_tree()"'


class XMLFile(Exportable, Importable):
    """
    Class for handling Read and Write operations on XML files.

    Attributes
    ----------
    path: Path | str
        System path to the file
    tree: ET.ElementTree | None
        Tree of the XML file
    root: ET.Element | None
        Root of the XML file

    Methods
    -------
    read() -> None
        Reads the XML file
    clear() -> None
        Clears all XML file data.
    gen_tree(root_name: str) -> None
        Generates a root and its tree for the XML file
    indent() -> str
        Indents the XML file
    write(content: dict[str, Any]) -> str
        Writes content to the XML file
    """
    def __init__(self, path: Path | str) -> None:
        """
        Initializes a XMLFile instance.

        Parameters
        ----------
        path: Path | str
            System path to file, it must end with '.xml'
        """
        super().__init__(path)
        if self.path.extension != '.xml':
            self.path.change_extension('.xml')
        self.tree: ET.ElementTree | None = None
        self.root: ET.Element | None = None

    def read(self) -> None:
        """
        Reads the XML file if it exists. Writes data into 'self.tree' and 'self.root'.
        """
        if self.path.exists:
            self.tree = ET.parse(self.path.absolute)
            self.root = self.tree.getroot()

    def clear(self) -> None:
        """
        Clears all XML file data, also resets 'self.tree' and 'self.root'.
        """
        super().clear()
        self.tree = None
        self.root = None

    def gen_tree(self, root_name: str) -> None:
        """
        Generates a root and its tree for the XML file

        Parameters
        ----------
        root_name: str
            Root name for the XML file
        """
        self.root = ET.Element(root_name)
        self.tree = ET.ElementTree(self.root)
        
    def indent(self) -> str:
        """
        Reads the XML file, converts into a string and indents it, then writes the file again.

        Returns
        -------
        str
            System absolute path to the new XML file
        """
        with open(self.path.absolute, 'r', encoding='utf-8') as file:
            element = ET.XML(file.read())
            ET.indent(element)
            datastr = ET.tostring(element, encoding='utf-8')
        with open(self.path.absolute, 'wb') as file:
            file.write(datastr)
        return self.path.absolute

    def write(self, content: dict[str, Any]) -> str:
        """
        Writes content to the XML file

        Parameters
        ----------
        content: dict[str, Any]
            Content to be written to the XML file

        Returns
        -------
        str
            System absolute path to the generated XML file

        Raises
        ------
        NoRootFound
            Raised if file has no Root
        """
        if self.root is None:
            raise NoRootFound
        user = ET.SubElement(self.root, 'user', {'Type': 'Consumer'})
        for key, value in content.items():
            if type(value) == str:
                ET.SubElement(user, key).text = value
            else:
                datatype = type_to_str.get(type(value))
                ET.SubElement(user, key, {'DataType': datatype}).text = str(value)
        self.tree.write(self.path.absolute, encoding='utf-8', xml_declaration=True)
        return self.path.absolute


# Tests
if __name__ == '__main__':
    f = XMLFile('../data/XMLTest.xml')
    f.gen_tree('SixerrData')
    print(f.write({'username': 'Juanpe777', 'nombre': 'Juan Pérez',
             'email': 'juanpe77@gmail.com', 'telefono': '+34 123 456 789',
             'posts': {Demand('Title1', 'Ejdesc', 'User1'),
                       Demand('Title2', 'Ejdesc', 'User2'),
                       Demand('Title3', 'Ejdesc', 'User3')},
             'metodo_de_pago': 'Paypal',
             'pocket': 122,
             'servicios_contratados': {Offer('Title1', 'Ejdesc', 'User1'),
                                       Offer('Title2', 'Ejdesc', 'User2'),
                                       Offer('Title3', 'Ejdesc', 'User3')}}))