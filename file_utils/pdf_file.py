"""
Module pdf_file.py

Defines class 'PDFFile(Exportable)' for writing PDF files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from dataclasses import dataclass
from typing import Optional, TypeVar
from textwrap3 import wrap
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import toColor
from reportlab.lib.utils import ImageReader


from file_utils import Path, Exportable


class AlignmentError(Exception):
    """
    Exception raised when an invalid alignment is entered in PDFFile class
    
    Attributes
    ----------
    align: str
        wrong alignment used
    """
    def __init__(self, align: str, *args) -> None:
        super().__init__(*args)
        self.align = align

    def __str__(self) -> str:
        return f'Alignment {self.align} does not exist. Supported alignments: "left", "right", "center"'


PDFContent = TypeVar('PDFContent', bound='PDFBase')


@dataclass
class Point:
    """
    Dataclass that represents a Point
    """
    x: float
    y: float

@dataclass
class PDFBase:
    """
    Dataclass that represents basic content for writing a PDF File
    """
    title: str
    description: str
    user: str
    image: Path | str
    category: str
    publication_date: datetime

@dataclass
class PDFOffer(PDFBase):
    """
    Dataclass with basic content and specific 'Offer' class content
    """
    price: float

@dataclass
class PDFDemand(PDFBase):
    """
    Dataclass with basic content and specific 'Demand' class content
    """
    urgency: int

class PDFFile(Exportable):
    """
    Class for handling Write operation on PDF files

    Attributes
    ----------
    path: Path | str
        System path to the file
    c: canvas
        ReportLab canvas object to write into a PDF file
    width: float
        Width of the PDF canvas
    height: float
        Height of the PDF canvas
    FONT: str
        (Class attribute), Typing font to be used
    FONT_SIZE: int
        (Class attribute), Typing font size to be used

    Methods
    -------
    add_textline(start_point: Point, text: str, align: str, color: Optional[str]) -> None
        Adds a text line to the PDF file
    add_paragraph(start_point: Point, text: str, width: int align: str, color: Optional[str]) -> float
        Adds one or more paragraph(s) to the PDF file
    draw_line(point1: Point, point2: Point, color: Optional[str]) -> None
        Draws a line to the PDF file
    draw_square(start_point: Point, width: int, height: int, color: Optional[str]) -> None
        Draws a rectangle to the PDF file
    add_image(image_path: Path | str, start_point: Point, height: int, width: int) -> None
        Adds an image to the PDF file
    change_font(new_font: Optional[str], new_font_size: Optional[int]) -> None
        Changes the font and its size
    write(content: PDFContent) -> None
        Writes content to a PDF file
    """
    def __init__(self, path: Path | str) -> None:
        """
        Initializes a PDFFile instance
        Generates a ReportLab canvas with a letter's pagesize.

        Parameters
        ----------
        path : Path | str
            System path to file, it must end with '.pdf'
        """
        super().__init__(path)
        if self.path.extension != '.pdf':
            self.path.change_extension('.pdf')
        self.c: canvas = canvas.Canvas(self.path.absolute, pagesize=letter)
        self.width, self.height = letter # Tamaño de la página

    def add_textline(self, start_point: Point, text: str, align: str, color: Optional[str] = 'rgb(0, 0, 0)') -> None:
        """
        Adds a text line to the PDF file, font and font size must be defined.
        'color' string must follow ReportLab's conventions, see ReportLab.lib.colors.toColor docstring.

        Parameters
        ----------
        start_point: Point
            Coordinates of the start of the text line
        text: str
            Text to be written
        align: str
            Alignment of the text line (Must be 'left', 'center' or 'right')
        color: Optional[str]
            Color of the text line, default is 'rgb(0, 0, 0)' / black

        Raises
        ------
        ValueError
            Color is not valid
        AlignmentError
            Alignment is not valid
        """
        self.c.setFillColor(toColor(color))
        self.c.setFont(type(self).FONT, type(self).FONT_SIZE)
        match align.lower():
            case 'left':
                self.c.drawString(start_point.x, start_point.y, text)
            case 'right':
                self.c.drawRightString(start_point.x, start_point.y, text)
            case 'center':
                self.c.drawCentredString(start_point.x, start_point.y, text)
            case _:
                raise AlignmentError(align)

    def add_paragraph(self, start_point: Point, text: str | list[str, ...], width: int, align: str,
                      color: Optional[str] = 'rgb(0, 0, 0)') -> float:
        """
        Adds one or more paragraph(s) (multiple lines) to a PDF file, font and font size must be defined.
        Calls 'PDFFile.add_textline' for every line.
        'color' string must follow ReportLab's conventions, see ReportLab.lib.colors.toColor docstring.

        Parameters
        ----------
        start_point: Point
            Coordinates of the start of the paragraph
        text: str | list[str, ...]
            Text to be written
        width: int
            Width of the paragraph
        align: str
            Alignment of the text line (Must be 'left', 'center' or 'right')
        color: Optional[str]
            Color of the text line, default is 'rgb(0, 0, 0)' / black

        Returns
        -------
        float
            Final 'Y' coordinate of the paragraph
        """
        text = text.splitlines() # FIXME: Si hay varios saltos de línea solo se muestra uno
        for i in text:
            paragraph = wrap(i, width)
            for line in paragraph:
                self.add_textline(start_point, line, align, color)
                start_point.y -= (type(self).FONT_SIZE + 2)
        return start_point.y

    def draw_line(self, point1: Point, point2: Point, color: Optional[str] = 'rgb(69, 114, 196)') -> None:
        """
        Draws a line to the PDF file.
        'color' string must follow ReportLab's conventions, see ReportLab.lib.colors.toColor docstring.

        Parameters
        ----------
        point1: Point
            Coordinates of the start of the line to be drawn
        point2: Point
            Coordinates of the end of the line to be drawn
        color: Optional[str]
            Color of the line, default is 'rgb(69, 114, 196)' / similar to lightblue

        Raises
        ------
        ValueError
            Color is not valid
        """
        self.c.setStrokeColor(toColor(color))
        self.c.line(point1.x, point1.y, point2.x, point2.y)

    def draw_square(self, start_point: Point, width: int, height: int, color: Optional[str] = 'rgb(211, 211, 211)') -> None:
        """
        Draws a rectangle on the PDF file.
        'color' string must follow ReportLab's conventions, see ReportLab.lib.colors.toColor docstring.

        Parameters
        ----------
        start_point: Point
            Coordinates of the start of the rectangle to be drawn
        width: int
            Width of the rectangle
        height: int
            Height of the rectangle
        color: Optional[str]
            Color of the rectangle, default is 'rgb(211, 211, 211)' / lightgrey

        Raises
        ------
        ValueError
            Color is not valid
        """
        self.c.setStrokeColor(toColor(color))
        self.c.rect(start_point.x, start_point.y, width, height)

    def add_image(self, image_path: Path | str, start_point: Point, height: int, width: int):
        """
        Adds an image to the PDF file.
        to avoid problems, 'image_path' should be an absolute path.
        If path is not found, a generic 'Image not found' is written instead.

        Parameters
        ----------
        image_path: Path | str
            Path to the image to be added (Absolute path is recommended)
        start_point: Point
            Coordinates of the start of the image to be added
        height: int
            Height of the image to be added
        width: int
            Width of the image to be added
        """
        try:
            image = ImageReader(image_path)
            self.c.drawImage(image, start_point.x, start_point.y, height, width)  # Ajusta la posición y el tamaño
        except IOError:
            self.add_textline(start_point, 'Imagen no encontrada', 'left')

    @classmethod
    def change_font(cls, new_font: Optional[str] = None, new_font_size: Optional[int] = None) -> None:
        """
        Changes typing font and size.
        Only changes the parameters that are introduced, e.g., introducing 'new_font' only changes the typing font.

        Parameters
        ----------
        new_font: Optional[str]
            New font of the file.
        new_font_size: Optional[int]
            New font size of the file.
        """
        if new_font is not None:
            cls.FONT = new_font
        if new_font_size is not None:
            cls.FONT_SIZE = new_font_size

    def write(self, content: PDFContent) -> str:
        """
        Writes content to a .pdf file

        Parameters
        ----------
        content : PDFContent
            Content to write

        Returns
        -------
        str
            System path to the generated file
        """
        # ===== CREACIÓN ARCHIVO PDF PUBLICACIÓN (OFERTA) =====
        height = self.height

        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        height -= 50
        self.add_textline(Point(50, height), 'Sixerr', 'left')

        # Título publicación
        type(self).change_font(new_font_size = 22)
        height -= 50
        self.add_textline(Point(self.width // 2 , height), content.title, 'center')
        height -= 20
        self.draw_line(Point(75, height), Point(525, height))

        # Usuario
        type(self).change_font('Helvetica', 12)
        height -= 30
        self.add_textline(Point(500, height), f'Publicado por: {content.user}', 'right')

        # Precio
        type(self).change_font(new_font_size=20)
        height -= 13
        self.add_textline(Point(100, height), f'{content.price}€', 'left', 'rgb(116, 175, 76)')

        # Fecha de publicación
        type(self).change_font(new_font_size = 8)
        height -= 7
        self.add_textline(Point(500, height), f'Fecha publicación: {content.publication_date.strftime("%d/%m/%Y")}', 'right')
        height -= 20
        self.draw_line(Point(75, height), Point(525, height))

        # Categoría
        height -= 30
        self.draw_square(Point(75, height), 200, 25)
        height += 10
        self.add_textline(Point(80, height), f'Categoría: {content.category}', 'left')

        # Descripción
        type(self).change_font(new_font_size=12)
        height -= 65
        height = self.add_paragraph(Point(75, height), content.description, 85, 'left')
        self.draw_line(Point(75, height), Point(525, height))

        # imagen
        height -= 150
        self.add_image(content.image, Point(250, height), 100, 100)

        # Guardado del archivo .pdf
        self.c.save()
        return self.path.absolute


# Tests
if __name__ == '__main__':
    f = PDFFile('archivo.pdf')
    # Lorem ipsum de ejemplo
    data_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Etiam fermentum tellus sed turpis auctor tempus. Nam massa arcu, feugiat quis dictum sit amet, sollicitudin ut lorem. Sed accumsan in enim at porta. Pellentesque dolor enim, aliquam ac libero vitae, porttitor laoreet neque. Suspendisse molestie eu metus sit amet tincidunt. Curabitur in arcu diam. Cras vel justo dictum, sollicitudin odio eu, maximus turpis. Nulla eget convallis velit. Maecenas metus velit, feugiat at pellentesque vitae, pellentesque id mi. Praesent suscipit ante quis elit lacinia, sit amet vehicula enim sollicitudin. Sed sit amet tempus sem. Ut iaculis elit quis ex dictum, nec tristique ipsum convallis."""
    pdf_content = PDFOffer(
        title='Titulo de Ejemplo',
        description=data_text,
        price=59.99,
        user='Usuario Ejemplo',
        image=Path('imagen.jpg').absolute,
        category='Clases particulares',
        publication_date=datetime.now(),
    )
    print(f.write(pdf_content))