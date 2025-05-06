"""
Module pdf_file.py

Defines class 'PDFFile(Exportable)' for writing PDF files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph # Parece ser otra manera de justificar texto sin textwrap


from file_utils import Path, Exportable

@dataclass
class LinePoint:
    x: float
    y: float

class Alineacion(Enum):
    izquierda: str = "left"
    derecha: str = "right"
    centrado: str = "center"


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

    def agregar_texto(self, start_point: LinePoint, text: str, align: str) -> None:
        """Escribir texto con diferentes alineaciones"""
        self.c.setFont(type(self).FONT, type(self).FONT_SIZE)
        match align.lower():
            case 'left':
                self.c.drawString(start_point.x, start_point.y, text)
            case 'right':
                self.c.drawRightString(start_point.x, start_point.y, text)
            case 'center':
                self.c.drawCentredString(start_point.x, start_point.y, text)
            case _:
                return Exception(f'Alignment {align} does not exist. Supported alignments: "left", "right", "center"')

    def dibujar_lineas(self, point1: LinePoint, point2: LinePoint):
        """Dibujar líneas de separación"""
        self.c.line(point1.x, point1.y, point2.x, point2.y)

    def dibujar_cuadros(self) -> None:
        """Dibujar rectángulos con colores de fondo, WIP"""
        # Rectángulo gris claro
        self.c.setFillColor(colors.lightgrey)
        self.c.rect(50, 600, 200, 50, fill=1)

        # Texto encima del rectángulo
        self.c.setFillColor(colors.black)
        self.c.drawString(60, 625, "Cuadro con texto")


    def anadir_imagen(self):
        """Añade imagenes al archivo, WIP"""
        try:
            imagen = ImageReader('imagen.jpg')
            self.c.drawImage(imagen, 400, 400, height=200, width=150)  # Ajusta la posición y el tamaño
        except Exception as e:
            self.c.drawString(400, 400, "Imagen no encontrada")

    @classmethod
    def change_font(cls, new_font: Optional[str] = None, new_font_size: Optional[int] = None) -> None:
        """
        Changes typing font and size
        """
        if new_font is not None:
            cls.FONT = new_font
        if new_font_size is not None:
            cls.FONT_SIZE = new_font_size


    def write(self, content: dict[str, str]) -> None:
        """
        Writes content to a .pdf file

        Parameters
        ----------
        content : dict[str]
            Content to write
        """
        # TODO: Obtener valores de 'content'
        # ===== CREACIÓN ARCHIVO PDF PUBLICACIÓN (OFERTA) =====
        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        self.agregar_texto(LinePoint(50, self.height - 50), 'Sixerr', 'left')

        # Título publicación
        type(self).change_font(new_font_size = 22)
        self.agregar_texto(LinePoint(self.width // 2 , self.height - 100), 'Titulo publicación', 'center')
        self.dibujar_lineas(LinePoint(50, self.height - 120), LinePoint(550, self.height - 120))

        # Precio
        type(self).change_font('Helvetica', 12)
        self.agregar_texto(LinePoint(500, self.height - 165), f'Precio: ${None}', 'right')

        # Usuario
        self.agregar_texto(LinePoint(500, self.height - 150), f'Publicado por: {None}', 'right')
            #TODO: Añadir imagen usuario (en caso de añadir imagenes a los perfiles)

        # Fecha de publicación
        type(self).change_font(new_font_size = 8)
        self.agregar_texto(LinePoint(500, self.height - 175), f'Fecha publicación: {None}', 'right')

        # Descripción
        type(self).change_font(new_font_size=12)
        # TODO: Implementar (mejor) el texto justificado
        text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam fermentum tellus sed turpis auctor tempus. Nam massa arcu, feugiat quis dictum sit amet, sollicitudin ut lorem. Sed accumsan in enim at porta. Pellentesque dolor enim, aliquam ac libero vitae, porttitor laoreet neque. Suspendisse molestie eu metus sit amet tincidunt. Curabitur in arcu diam. Cras vel justo dictum, sollicitudin odio eu, maximus turpis. Nulla eget convallis velit. Maecenas metus velit, feugiat at pellentesque vitae, pellentesque id mi. Praesent suscipit ante quis elit lacinia, sit amet vehicula enim sollicitudin. Sed sit amet tempus sem. Ut iaculis elit quis ex dictum, nec tristique ipsum convallis."""
        wrapped_text = textwrap.fill(text, width=80)
        splitted_text = wrapped_text.split('\n')
        height = self.height - 230
        for i in splitted_text:
            self.agregar_texto(LinePoint(100, height), i, 'left')
            height -= 14 # TODO: Modificar una variable local 'height' en vez de utilizar siempre 'self.height - ...'

        # Guardado del archivo .pdf
        self.c.save()
        print(f"PDF '{self.filename}' generado con éxito.")


# Tests
if __name__ == '__main__':
    f = PDFFile('archivo.pdf')
    f.write({'a': 'a'})