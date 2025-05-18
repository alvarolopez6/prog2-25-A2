"""
file_utils package

Package containing the files necessary to handle file paths and file writes and reads.
Supported file formats: csv, xml, pdf

Classes
-------
Path (.path.py)
    Basic Class for handling system paths

File (.file.py)
    Basic Class for handling file operations
Importable (.file.py)
    Abstract Class for files that can be read
Exportable (.file.py)
    Abstract Class for files that can be written

CSVFile (.csv_file.py)
    Class for operations on CSV files

PDFFile - (.pdf_file.py)
    Class for operations on PDF files
PDFOffer, PDFDemand, PDFConsumer, PDFFreelancer - (.pdf_file.py)
    Dataclasses with variables needed for writing PDF files

XMLFile - Not Implemented yet (.xml_file.py)
    Class for operations on XML files
"""

from .path import Path
from .file import File, Importable, Exportable
from .csv_file import CSVFile
from .pdf_file import PDFFile, PDFOffer, PDFDemand, PDFConsumer, PDFFreelancer
from .xml_file import XMLFile