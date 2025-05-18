"""
Module xml_file.py

Defines class 'XMLFile(Exportable, Importable)' for writing XML files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from typing import Any
from file_utils import Path, Exportable, Importable
import xml.etree.ElementTree as ET
import ast


type_to_str = {
    type(None): 'None',
    int: 'int',
    float: 'float',
    bool: 'bool',
    dict: 'dict',
    list: 'list',
    tuple: 'tuple',
    set: 'set'
}

str_to_type = {
    'None': type(None),
    'int': int,
    'float': float,
    'bool': bool,
    'dict': dict,
    'list': list,
    'tuple': tuple,
    'set': set
}


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
    data: dict[str, Any] | None
        Dictionary with XML file's data.

    Methods
    -------
    str_to_data(value: str, data_type: str) -> Any:
        Converts a string to a specified data type.
    read() -> dict[str, Any]:
        Reads the XML file and saves file's data.
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
        self.data: dict[str, Any] | None = None

    @staticmethod
    def str_to_data(value: str, data_type: type) -> Any:
        """
        Converts a string to a specified data type.

        Parameters
        ----------
        value: str
            The string value to be converted.
        data_type: type
            The target data type.

        Returns
        -------
        Any
            The converted value.

        Raises
        ------
        ValueError
            If the conversion fails
        """
        # Si es booleano, int/float o str, la conversión es directa
        if data_type is bool:
            return value.lower() == 'true'
        if data_type in {int, float, str}:
            return data_type(value)

        # En caso de no serlo, utilizamos la libreria 'ast' para la conversión
        try:
            evaluated = ast.literal_eval(value)
            if data_type is set: # 'literal_eval' devuelve listas o tuplas, si buscamos set, lo convertimos
                return set(evaluated)
            else:
                return evaluated # En caso contrario, devolvemos el valor directamente
        except (ValueError, TypeError) as e:
            raise ValueError(f'Conversion error: {e}')

    def read(self) -> dict[str, Any]:
        """
        Reads the XML file if it exists. Returns all data in a dict, also saves all data in 'self.data'
        XML elements must have 'DataType' attribute if the target data type is not 'str' to be converted.

        Returns
        -------
        dict[str, Any]
            Dictionary with the file data.

        Raises
        ------
        NoRootFound
            If the XML file has no root
        ValueError
            If XML file has no main element as 'user' or 'post'
            or an Unknown data type is found.
        """
        if self.path.exists:
            self.tree = ET.parse(self.path.absolute)
            self.root = self.tree.getroot()
            if self.root is None:
                raise NoRootFound

        for tag in ('user', 'post'):
            main_element = self.root.find(tag)
            if main_element is not None:
                break

        if main_element is None:
            raise ValueError('XML File has no main element as "user" or "post"')

        data = {'type': main_element.get('Type')}
        for child in main_element:
            data_type_str = child.get('DataType')
            if data_type_str is None:
                # data_type_type == str
                data[child.tag] = child.text
                continue
            data_type = str_to_type.get(data_type_str)
            if data_type is None:
                raise ValueError(f'Unknown data type: {data_type_str}')
            data[child.tag] = self.str_to_data(child.text, data_type)

        self.data = data
        return self.data

    def clear(self) -> None:
        """
        Clears all XML file data, also resets 'self.tree', 'self.root' and 'self.data'.
        """
        super().clear()
        self.tree = None
        self.root = None
        self.data = None

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
        tree_tag = 'user' if content.get('type') in {'Consumer', 'Freelancer'} else 'post'
        tree = ET.SubElement(self.root, tree_tag, {'Type': content.get('type')})
        for key, value in content.items():
            if key == 'type':
                continue
            if type(value) == str:
                ET.SubElement(tree, key).text = value
            else:
                datatype = type_to_str.get(type(value))
                ET.SubElement(tree, key, {'DataType': datatype}).text = str(value)
        self.tree.write(self.path.absolute, encoding='utf-8', xml_declaration=True)
        return self.path.absolute


# Tests
if __name__ == '__main__':
    from demand import Demand
    from offer import Offer

    # XML for Users
    f = XMLFile('../data/XMLTest.xml')
    f.gen_tree('SixerrData')
    print(f.write({'type': 'Consumer', 'username': 'Juanpe777', 'nombre': 'Juan Pérez',
             'email': 'juanpe77@gmail.com', 'telefono': '+34 123 456 789',
             'posts': {Demand('Title1', 'Ejdesc', 'User1').title,
                       Demand('Title2', 'Ejdesc', 'User2').title,
                       Demand('Title3', 'Ejdesc', 'User3').title},
             'metodo_de_pago': 'Paypal',
             'pocket': 122,
             'servicios_contratados': {Offer('Title1', 'Ejdesc', 'User1').title,
                                       Offer('Title2', 'Ejdesc', 'User2').title,
                                       Offer('Title3', 'Ejdesc', 'User3').title}}))
    f.indent()
    for k, v in f.read().items():
         print(f'Key: {k}, Value: {v}, ValueType: {type(v)}')

    print('\n')

    # XML for Posts
    f2 = XMLFile('../data/XMLTestPost.xml')
    f2.gen_tree('SixerrData')
    print(f2.write({'type': 'Demand', 'title': 'Titulo1', 'description': 'Ejdesc1', 'user': 'Juanpe777',
                   'urgency': 3, 'publication_date': '25/05/2025', 'category': 'Clases particulares'}))
    f2.indent()
    for k,v in f2.read().items():
        print(f'Key: {k}, Value: {v}, ValueType: {type(v)}')