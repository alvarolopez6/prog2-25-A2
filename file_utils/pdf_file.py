"""
Module pdf_file.py

Defines class 'PDFFile(File)' for writing PDF files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from dataclasses import dataclass
from enum import Enum

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from file_utils import Path, File

@dataclass
class LinePoint:
    x: int
    y: int

class Alineacion(Enum):
    izquierda: str = "left"
    derecha: str = "right"
    centrado: str = "center"


class PDFFile(File):
    """
    Class for handling Write operation on PDF files

    Attributes
    ----------
    path: Path | str
        System path to the file
    """

    FONT_SIZE = 14
    FONT = 'Helvetica-Bold'

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

    def agregar_texto(self, alineacion: Alineacion, text: str, font: str = FONT, font_size: int = FONT_SIZE):
        """Escribir texto con diferentes alineaciones"""
        # TODO: Realmente es necesario hacer la asignación c = self.c? Comprobar si funciona igual al quitarlo
        c = self.c
        c.setFont(font, font_size)
        if alineacion == Alineacion.izquierda:
            c.drawString(50, 750, "Texto alineado a la izquierda")
        elif alineacion == Alineacion.derecha:
            c.drawRightString(550, 730, "Texto alineado a la derecha")
        elif alineacion == Alineacion.centrado:
            c.drawCentredString(300, 710, "Texto centrado")
        else:
            raise Exception("Alineación incorrecta")

    def dibujar_lineas(self, point1: LinePoint, point2: LinePoint):
        """Dibujar líneas de separación"""
        c = self.c
        c.setStrokeColor(colors.black)
        c.line(point1.x, point1.y, point2.x, point2.y)
        c.line(50, 700, 550, 700)  # Línea horizontal
        c.line(50, 680, 50, 500)   # Línea vertical
        c.line(50, 500, 550, 700)  # Línea diagonal

    def dibujar_cuadros(self):
        """Dibujar rectángulos con colores de fondo y texto encima"""
        c = self.c

        # Rectángulo gris claro
        c.setFillColor(colors.lightgrey)
        c.rect(50, 600, 200, 50, fill=1)

        # Texto encima del rectángulo
        c.setFillColor(colors.black)
        c.drawString(60, 625, "Cuadro con texto")

        # Otro rectángulo azul
        c.setFillColor(colors.lightblue)
        c.rect(300, 600, 200, 50, fill=1)

        # Texto encima del segundo rectángulo
        c.setFillColor(colors.black)
        c.drawString(310, 625, "Otro cuadro con texto")

    def anadir_imagen(self):
        c = self.c
        try:
            imagen = ImageReader('imagen.jpg')
            c.drawImage(imagen, 400, 400, height=200, width=150)  # Ajusta la posición y el tamaño
        except Exception as e:
            c.drawString(400, 400, "Imagen no encontrada")

    def write(self, content: str) -> None:
        """
        TODO: Writes content to a PDF file

        Parameters
        ----------
        content : str
            Content to write
        """
        self.agregar_texto(Alineacion.izquierda, 'Texto prueba')
        self.dibujar_lineas(LinePoint(0, 0), LinePoint(0, 0))
        self.dibujar_cuadros()
        self.anadir_imagen()
        self.c.save()
        print(f"PDF '{self.filename}' generado con éxito.")


    def read(self) -> NotImplementedError:
        """
        Reading PDF files is not implemented.

        Returns
        -------
        NotImplementedError
        """
        return NotImplementedError('PDF file reading is not implemented.')
