"""
Module pdf_file.py

Defines class 'PDFFile(Exportable)' for writing PDF files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from dataclasses import dataclass
from typing import Optional, TypeVar

import textwrap
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
# TODO: No utilizar 'colors', crear colores usando RGB con 'toColor' (pedirlo por parámetro, Optional[str])
from reportlab.lib.colors import toColor
from reportlab.lib.utils import ImageReader
#from reportlab.platypus import SimpleDocTemplate, Paragraph # Parece ser otra manera de justificar texto sin textwrap

from file_utils import Path, Exportable


class AlignmentError(Exception):
    """
    Exception raised when an invalid alignment is entered in PDFFile class
    """
    def __init__(self, align: str, *args) -> None:
        super().__init__(*args)
        self.align = align

    def __str__(self) -> str:
        return f'Alignment {self.align} does not exist. Supported alignments: "left", "right", "center"'

PDFContent = TypeVar('PDFContent', bound='PDFBase')

@dataclass
class LinePoint:
    x: float
    y: float

@dataclass
class PDFBase:
    title: str
    description: str
    user: str
    image: Path | str
    category: str
    publication_date: datetime

@dataclass
class PDFOffer(PDFBase):
    price: float

@dataclass
class PDFDemand(PDFBase):
    urgency: int

class PDFFile(Exportable):
    """
    Class for handling Write operation on PDF files

    Attributes
    ----------
    path: Path | str
        System path to the file
    """
    def __init__(self, path: Path | str) -> None:
        """
        Initializes a PDFFile instance

        Parameters
        ----------
        path : Path | str
            System path to file, it must end with '.pdf'
        """
        super().__init__(path)
        if self.path.extension != '.pdf':
            self.path.change_extension('.pdf')
        self.filename = 'archivo.pdf' #TODO: Poner correctamente el nombre del archivo
        self.c = canvas.Canvas(self.filename, pagesize=letter)
        self.width, self.height = letter # Tamaño de la página

    def add_textline(self, start_point: LinePoint, text: str, align: str) -> None:
        """Escribir texto con diferentes alineaciones"""
        self.c.setStrokeColor(colors.black)
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

    def draw_line(self, point1: LinePoint, point2: LinePoint):
        """Dibujar líneas de separación"""
        self.c.setStrokeColor(toColor('rgb(69, 114, 196)'))
        self.c.line(point1.x, point1.y, point2.x, point2.y)

    def draw_square(self, start_point: LinePoint, width: int, height: int) -> None:
        """Dibujar rectángulos con colores de fondo, WIP"""
        # Rectángulo gris claro
        self.c.setStrokeColor(colors.lightgrey)
        self.c.rect(start_point.x, start_point.y, width, height)

    def add_image(self, image_path: Path | str, start_point: LinePoint, height: int, width: int):
        """Añade imagenes al archivo, WIP"""
        try:
            image = ImageReader(image_path)
            self.c.drawImage(image, start_point.x, start_point.y, height, width)  # Ajusta la posición y el tamaño
        except IOError:
            self.add_textline(start_point, 'Imagen no encontrada', 'left')

    @classmethod
    def change_font(cls, new_font: Optional[str] = None, new_font_size: Optional[int] = None) -> None:
        """
        Changes typing font and size
        """
        if new_font is not None:
            cls.FONT = new_font
        if new_font_size is not None:
            cls.FONT_SIZE = new_font_size

    def write(self, content: PDFContent) -> None:
        """
        Writes content to a .pdf file

        Parameters
        ----------
        content : PDFContent
            Content to write
        """
        # ===== CREACIÓN ARCHIVO PDF PUBLICACIÓN (OFERTA) =====
        height = self.height
        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        height -= 50
        self.add_textline(LinePoint(50, height), 'Sixerr', 'left')

        # Título publicación
        type(self).change_font(new_font_size = 22)
        height -= 50
        self.add_textline(LinePoint(self.width // 2 , height), content.title, 'center')
        height -= 20
        self.draw_line(LinePoint(75, height), LinePoint(525, height))

        # Usuario
        type(self).change_font('Helvetica', 12)
        height -= 30
        self.add_textline(LinePoint(500, height), f'Publicado por: {content.user}', 'right')

        # Precio
        type(self).change_font(new_font_size=20)
        self.add_textline(LinePoint(100, height), f'{content.price}€', 'left')

        # Fecha de publicación
        type(self).change_font(new_font_size = 8)
        height -= 20
        self.add_textline(LinePoint(500, height), f'Fecha publicación: {content.publication_date.strftime("%d/%m/%Y")}', 'right')
        height -= 20
        self.draw_line(LinePoint(75, height), LinePoint(525, height))

        # Categorias, WIP
        height -= 30
        self.draw_square(LinePoint(75, height), 200, 25)
        height += 10
        self.add_textline(LinePoint(75, height), f'Categoría: {content.category}', 'left')

        # Descripción TODO: Implementar (mejor) el texto justificado
        type(self).change_font(new_font_size=12)
        wrapped_text = textwrap.fill(content.description, width=85)
        splitted_text = wrapped_text.split('\n')
        height -= 65
        for i in splitted_text:
            self.add_textline(LinePoint(75, height), i, 'left')
            height -= 14
        self.draw_line(LinePoint(75, height), LinePoint(525, height))

        # Prueba imagen, WIP
        height -= 150
        self.add_image(content.image, LinePoint(75, height), 100, 100)

        # Guardado del archivo .pdf
        self.c.save()
        print(f"PDF '{self.filename}' generado con éxito.")


# Tests
if __name__ == '__main__':
    f = PDFFile('archivo.pdf')
    # Lorem ipsum de ejemplo
    data_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam fermentum tellus sed turpis auctor tempus. Nam massa arcu, feugiat quis dictum sit amet, sollicitudin ut lorem. Sed accumsan in enim at porta. Pellentesque dolor enim, aliquam ac libero vitae, porttitor laoreet neque. Suspendisse molestie eu metus sit amet tincidunt. Curabitur in arcu diam. Cras vel justo dictum, sollicitudin odio eu, maximus turpis. Nulla eget convallis velit. Maecenas metus velit, feugiat at pellentesque vitae, pellentesque id mi. Praesent suscipit ante quis elit lacinia, sit amet vehicula enim sollicitudin. Sed sit amet tempus sem. Ut iaculis elit quis ex dictum, nec tristique ipsum convallis."""
    pdf_content = PDFOffer(
        title='Titulo de Ejemplo',
        description=data_text,
        price=59.99,
        user='Usuario Ejemplo',
        image='imagen.jpg',
        category='Clases particulares',
        publication_date=datetime.now(),
    )
    f.write(pdf_content)