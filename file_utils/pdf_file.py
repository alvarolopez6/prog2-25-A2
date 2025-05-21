"""
Module pdf_file.py

Defines class 'PDFFile(Exportable)' and dataclasses 'PDFContent' for writing PDF files

Author: Ismael Escribano
Creation Date: 05-05-2025
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import reduce
from typing import Optional, Union, TYPE_CHECKING

from textwrap3 import wrap
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import toColor
from reportlab.lib.utils import ImageReader


from file_utils import Path, Exportable

if TYPE_CHECKING:
    from post.generic_posts import Post
    from post.demand import Demand
    from post.offer import Offer

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


@dataclass
class Point:
    """
    Dataclass that represents a Point

    Parameters
    ----------
    x: float
        X coordinate
    y: float
        Y coordinate
    """
    x: float
    y: float

@dataclass
class PDFPost:
    """
    Dataclass that represents basic content for writing a PDF File for Sixerr Posts

    Parameters
    ----------
    title: str
        Title of the post
    description: str
        Description of the post
    user: str
        User who publishes the content.
    image: Path | str
        Image associated with the post
    category: str
        Category associated with the post
    publication_date: datetime
        Date the post was published
    """
    title: str
    description: str
    user: str
    image: Path | str
    category: str
    publication_date: datetime

@dataclass
class PDFOffer(PDFPost):
    """
    Dataclass with basic Sixerr Post content and specific 'Offer' class content

    Parameters
    ----------
    price: float
        Price of the offer
    """
    price: float

@dataclass
class PDFDemand(PDFPost):
    """
    Dataclass with basic content and specific 'Demand' class content

    Parameters
    ----------
    urgency: int
        Level of urgency (from 1 to 5)
    """
    urgency: int

@dataclass
class PDFUser:
    """
    Dataclass with basic content for writing a PDF File for User profiles

    Parameters
    ----------
    username: str
        a unique string used to identify the user
    nombre: str
        name of the user
    email: str
        email of the user
    telefono: str
        phone number of the user
    posts: set[Post]
        list with all Post created by the user
    money: float
        Consumer's remaining virtual pocket balance
    """
    username: str
    nombre: str
    email: str
    telefono: str
    posts: set[Post]
    money: float


@dataclass
class PDFFreelancer(PDFUser):
    """
    Dataclass with basic content and specific 'Freelancer' class content

    Parameters
    ----------
    habilidades: list[str]
        list with all the perks that the freelancer have
    opiniones: list[int]
        list with all the ratings of the costumers
    rating: float
        rating of the freelancer
    """
    habilidades: list[str]
    opiniones: list[int]
    rating: float

@dataclass
class PDFConsumer(PDFUser):
    """
    Dataclass with basic content and specific 'Consumer' class content

    Parameters
    ----------
    metodo_de_pago: str
        Consumer's payment method
    servicios_contratados: set[Offer]
        List with all Offers hired by the Consumer
    """
    metodo_de_pago: str
    servicios_contratados: set[Offer]


PDFContent = Union[PDFOffer, PDFDemand, PDFFreelancer, PDFConsumer]


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
    sixerr_logo: Path
        (Class attribute), System path to 'sixerr_logo.png'
    FONT: str
        (Class attribute), Typing font to be used
    FONT_SIZE: int
        (Class attribute), Typing font size to be used

    Methods
    -------
    __add_textline(start_point: Point, text: str, align: str, color: Optional[str]) -> None
        Adds a text line to the PDF file
    __add_paragraph(start_point: Point, text: str, width: int align: str, color: Optional[str]) -> float
        Adds one or more paragraph(s) to the PDF file
    __draw_line(point1: Point, point2: Point, color: Optional[str]) -> None
        Draws a line to the PDF file
    __draw_square(start_point: Point, width: int, height: int, color: Optional[str]) -> None
        Draws a rectangle to the PDF file
    __add_image(image_path: Path | str, start_point: Point, height: int, width: int) -> None
        Adds an image to the PDF file
    __change_font(new_font: Optional[str], new_font_size: Optional[int]) -> None
        Changes the font and its size
    __generate_offer(content: PDFOffer) -> None
        Creates a PDF file for Sixerr Offer
    __generate_demand(content: PDFDemand) -> None
        Creates a PDF file for Sixerr Demand
    __generate_freelancer_profile(content: PDFFreelancer) -> None
        Creates a PDF file for Sixerr Freelancer
    __generate_consumer_profile(content: PDFConsumer) -> None
        Creates a PDF file for Sixerr Consumer
    write(content: PDFContent) -> None
        Writes content to a PDF file
    """
    sixerr_logo = Path('./data/images/sixerrlogo.png').absolute

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

    def __add_textline(self, start_point: Point, text: str, align: str, color: Optional[str] = 'rgb(0, 0, 0)') -> None:
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

    def __add_paragraph(self, start_point: Point, text: str, width: int, align: str,
                      color: Optional[str] = 'rgb(0, 0, 0)') -> float:
        """
        Adds one or more paragraph(s) (multiple lines) to a PDF file, font and font size must be defined.
        Calls 'PDFFile.__add_textline' for every line.
        'color' string must follow ReportLab's conventions, see ReportLab.lib.colors.toColor docstring.

        Parameters
        ----------
        start_point: Point
            Coordinates of the start of the paragraph
        text: str
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
        text = text.splitlines()
        for i in text:
            if i.strip() == '':
                start_point.y -= type(self).FONT_SIZE + 2
            else:
                paragraph = wrap(i, width)
                for line in paragraph:
                    self.__add_textline(start_point, line, align, color)
                    start_point.y -= type(self).FONT_SIZE + 2
        return start_point.y

    def __draw_line(self, point1: Point, point2: Point, color: Optional[str] = 'rgb(69, 114, 196)') -> None:
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

    def __draw_square(self, start_point: Point, width: int, height: int, color: Optional[str] = 'rgb(211, 211, 211)') -> None:
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

    def __add_image(self, image_path: Path | str, start_point: Point, height: int, width: int) -> None:
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
            self.__add_textline(start_point, 'Imagen no encontrada', 'left')

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

    def __generate_offer(self, content: PDFOffer) -> None:
        """
        Creates a PDF File using a template for 'Sixerr (Post) offer'

        Parameters
        ----------
        content: PDFOffer
            Content of the Post to be written
        """
        height = self.height

        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        height -= 100
        self.__add_image(self.sixerr_logo, Point(50, height), 100, 100)

        # Tipo de post
        type(self).change_font('Helvetica', 12)
        self.__add_textline(Point(550, height + 50), 'Oferta', 'right')

        # Título publicación
        type(self).change_font(new_font_size=22)
        height -= 20
        self.__add_textline(Point(self.width // 2, height), content.title, 'center')
        height -= 20
        self.__draw_line(Point(75, height), Point(525, height))

        # Usuario
        type(self).change_font('Helvetica', 12)
        height -= 30
        self.__add_textline(Point(500, height), f'Publicado por: {content.user}', 'right')

        # Precio
        type(self).change_font(new_font_size=20)
        height -= 13
        self.__add_textline(Point(100, height), f'{content.price}€', 'left', 'rgb(116, 175, 76)')

        # Fecha de publicación
        type(self).change_font(new_font_size=8)
        height -= 7
        self.__add_textline(Point(500, height), f'Fecha publicación: {content.publication_date.strftime("%d/%m/%Y")}',
                            'right')
        height -= 20
        self.__draw_line(Point(75, height), Point(525, height))

        # Categoría
        height -= 30
        self.__draw_square(Point(75, height), 200, 25)
        height += 10
        self.__add_textline(Point(80, height), f'Categoría: {content.category}', 'left')

        # Descripción
        type(self).change_font(new_font_size=12)
        height -= 65
        height = self.__add_paragraph(Point(75, height), content.description, 85, 'left')
        self.__draw_line(Point(75, height), Point(525, height))

        # imagen
        height -= 150
        self.__add_image(content.image, Point(250, height), 100, 100)


    def __generate_demand(self, content: PDFDemand) -> None:
        """
        Creates a PDF File using a template for 'Sixerr (Post) demand'

        Parameters
        ----------
        content: PDFDemand
            Content of the Post to be written
        """
        height = self.height

        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        height -= 100
        self.__add_image(self.sixerr_logo, Point(50, height), 100, 100)

        # Tipo de post
        type(self).change_font('Helvetica', 12)
        self.__add_textline(Point(550, height + 50), 'Demanda', 'right')

        # Título publicación
        type(self).change_font(new_font_size=22)
        height -= 20
        self.__add_textline(Point(self.width // 2, height), content.title, 'center')
        height -= 20
        self.__draw_line(Point(75, height), Point(525, height), 'rgb(34, 139, 34)')

        # Usuario
        type(self).change_font('Helvetica', 12)
        height -= 15
        self.__add_textline(Point(75, height), f'Publicado por: {content.user}', 'left')

        # Fecha de publicación
        type(self).change_font(new_font_size=8)
        self.__add_textline(Point(500, height), f'Fecha publicación: {content.publication_date.strftime("%d/%m/%Y")}',
                            'right')

        # Urgencia
        type(self).change_font(new_font_size=12)
        height -= 25
        urgency_info = {1: ['Muy baja', 'rgb(0, 51, 102)'], 2: ['Baja', 'rgb(0, 102, 204)'],
                        3: ['Intermedia', 'rgb(0, 153, 153)'], 4: ['Alta', 'rgb(255, 153, 51)'],
                        5: ['Muy alta', 'rgb(204, 0, 0)']}
        urgency_str, color = urgency_info.get(content.urgency)
        self.__add_textline(Point(75, height),
                            f'Urgencia: {urgency_str} ({content.urgency})',
                            'left', color)

        height -= 15
        self.__draw_line(Point(75, height), Point(525, height), 'rgb(34, 139, 34)')

        # Categoría
        height -= 30
        self.__draw_square(Point(75, height), 200, 25)
        height += 10
        self.__add_textline(Point(80, height), f'Categoría: {content.category}', 'left')

        # Descripción
        type(self).change_font(new_font_size=12)
        height -= 50
        height = self.__add_paragraph(Point(75, height), content.description, 85, 'left')
        self.__draw_line(Point(75, height), Point(525, height), 'rgb(34, 139, 34)')

        # imagen
        height -= 150
        self.__add_image(content.image, Point(250, height), 100, 100)


    def __generate_freelancer_profile(self, content: PDFFreelancer) -> None:
        """
        Creates a PDF File using a template for 'Sixerr (User) freelancer'

        Parameters
        ----------
        content: PDFFreelancer
            Content of the Post to be written
        """
        height = self.height

        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        height -= 100
        self.__add_image(self.sixerr_logo, Point(50, height), 100, 100)

        # Información del usuario
        # Nombre
        type(self).change_font(new_font_size=18)
        height -= 20
        self.__add_textline(Point(75, height), content.nombre, 'left')

        # Username
        type(self).change_font('Helvetica', new_font_size=12)
        height -= 20
        self.__add_textline(Point(75, height), content.username, 'left', 'rgb(128, 128, 128)')

        # Tipo de cuenta
        type(self).change_font(new_font_size=14)
        height -= 30
        self.__add_textline(Point(75, height), 'Tipo de cuenta: Freelancer', 'left')

        # Email
        type(self).change_font(new_font_size=12)
        height += 42
        self.__add_textline(Point(550, height), f'Email: {content.email}', 'right')

        # Teléfono
        height -= 20
        self.__add_textline(Point(550, height), f'Teléfono: {content.telefono}', 'right')

        # Saldo
        height -= 20
        self.__add_textline(Point(550, height), f'Saldo disponible: {content.money}€', 'right')

        height -= 22
        self.__draw_line(Point(75, height), Point(550, height))

        # Habilidades
        type(self).change_font(new_font_size=14)
        height -= 20
        if type(content.habilidades) == type(None):
            self.__add_textline(Point(75, height), f'Habilidades: No hay habilidades indicadas actualmente', 'left')
            height -= 20
        else:
            habilidades_str = reduce(lambda x, y: x + ', ' + y, content.habilidades)
            height = self.__add_paragraph(Point(75, height), f'Habilidades: {habilidades_str}', 90, 'left')

        # Reseñas
        height -= 20
        review_color = {3: 'rgb(178, 34, 34)', 5: 'rgb(255, 165, 0)',
                        7: 'rgb(204, 204, 0)', 9: 'rgb(0, 128, 0)', 10: 'rgb(100, 200, 100)'}
        for key in review_color.keys():
            if content.rating <= key:
                color = review_color[key]
                break
        else:
            color = 'rgb(0, 0, 0)'
        self.__add_textline(Point(75, height), f'{content.rating} de Valoración', 'left', color)

        height -= 20
        self.__draw_line(Point(75, height), Point(550, height))

        # Posts creados
        height -= 20
        self.__add_textline(Point(75, height), f'Posts de {content.nombre}:', 'left')

        height -= 20
        if len(content.posts) == 0:
            self.__add_textline(Point(75, height), 'El usuario no tiene posts creados.', 'left')
        else:
            posts_names = map(lambda x: x.title, content.posts)
            posts_str = reduce(lambda x, y: x + '\n- ' + y, set(posts_names))
            self.__add_paragraph(Point(75, height), '- ' + posts_str, 100, 'left')

    def __generate_consumer_profile(self, content: PDFConsumer) -> None:
        """
        Creates a PDF File using a template for 'Sixerr (User) Consumer'

        Parameters
        ----------
        content: PDFConsumer
            Content of the Post to be written
        """
        height = self.height

        # Logo Sixerr
        type(self).change_font('Helvetica-Bold', 16)
        height -= 100
        self.__add_image(self.sixerr_logo, Point(50, height), 100, 100)

        # Información del usuario
        # Nombre
        type(self).change_font(new_font_size=18)
        height -= 20
        self.__add_textline(Point(75, height), content.nombre, 'left')

        # Username
        type(self).change_font('Helvetica', new_font_size=12)
        height -= 20
        self.__add_textline(Point(75, height), content.username, 'left', 'rgb(128, 128, 128)')

        # Tipo de cuenta
        type(self).change_font(new_font_size=14)
        height -= 30
        self.__add_textline(Point(75, height), 'Tipo de cuenta: Consumer', 'left')

        # Email
        type(self).change_font(new_font_size=12)
        height += 55
        self.__add_textline(Point(550, height), f'Email: {content.email}', 'right')

        # Teléfono
        height -= 20
        self.__add_textline(Point(550, height), f'Teléfono: {content.telefono}', 'right')

        # Método de pago
        height -= 20
        self.__add_textline(Point(550, height), f'Método de pago: {content.metodo_de_pago}', 'right')

        # Saldo
        height -= 20
        self.__add_textline(Point(550, height), f'Saldo disponible: {content.money}€', 'right')

        height -= 22
        self.__draw_line(Point(75, height), Point(550, height), color='rgb(113, 173, 72)')

        # Posts creados (demandas)
        height -= 20
        self.__add_textline(Point(75, height), f'Servicios solicitados por {content.nombre}:', 'left')

        height -= 20
        if len(content.posts) == 0:
            self.__add_textline(Point(75, height), 'El usuario no tiene posts creados.', 'left')
            height -= 20
        else:
            posts_names = map(lambda x: x.title, content.posts)
            posts_str = reduce(lambda x, y: x + '\n- ' + y, set(posts_names))
            height = self.__add_paragraph(Point(75, height), '- ' + posts_str, 100, 'left')

        self.__draw_line(Point(75, height), Point(550, height), color='rgb(113, 173, 72)')

        # Servicios contratados
        height -= 20
        self.__add_textline(Point(75, height), f'Servicios contratados por {content.nombre}:', 'left')

        height -= 20
        if len(content.servicios_contratados) == 0:
            self.__add_textline(Point(75, height), 'El usuario no tiene servicios contratados.', 'left')
        else:
            services_str = str()
            for post in content.servicios_contratados:
                services_str += f'- {post.title} (Creado por: {post.user})\n'
            self.__add_paragraph(Point(75, height), services_str, 100, 'left')

    def write(self, content: PDFContent) -> str:
        """
        Writes content to a .pdf file.
        Calls a '__generate_X' method according to the content instance type

        Parameters
        ----------
        content : PDFContent
            Content to write

        Returns
        -------
        str
            System absolute path to the generated file

        Raises
        ------
        TypeError
            If 'content' is not a PDFContent instance
        """
        if isinstance(content, PDFOffer):
            self.__generate_offer(content)
        elif isinstance(content, PDFDemand):
            self.__generate_demand(content)
        elif isinstance(content, PDFFreelancer):
            self.__generate_freelancer_profile(content)
        elif isinstance(content, PDFConsumer):
            self.__generate_consumer_profile(content)
        else:
            raise TypeError('Content to be written must be a "PDFContent" instance')
        # Guardado del archivo .pdf
        self.c.save()
        return self.path.absolute


# Tests
if __name__ == '__main__':
    from post.demand import Demand
    from post.offer import Offer
    # Lorem ipsum de ejemplo
    data_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Etiam fermentum tellus sed turpis auctor tempus. Nam massa arcu, feugiat quis dictum sit amet, sollicitudin ut lorem. 

Sed accumsan in enim at porta. Pellentesque dolor enim, aliquam ac libero vitae, porttitor laoreet neque. Suspendisse molestie eu metus sit amet tincidunt. Curabitur in arcu diam. Cras vel justo dictum, sollicitudin odio eu, maximus turpis. Nulla eget convallis velit. Maecenas metus velit, feugiat at pellentesque vitae, pellentesque id mi. Praesent suscipit ante quis elit lacinia, sit amet vehicula enim sollicitudin. Sed sit amet tempus sem. Ut iaculis elit quis ex dictum, nec tristique ipsum convallis."""

    # OFERTA
    f = PDFFile('../data/OfferTest.pdf')
    pdf_content = PDFOffer(
       title='Titulo de Ejemplo',
       description=data_text,
       price=59.99,
       user='Usuario Ejemplo',
       image=Path('imagen.jpg').absolute,
       category='Clases particulares',
       publication_date=datetime.now())
    print('PDF Generado en:')
    print(f.write(pdf_content))

    # DEMANDA
    f2 = PDFFile('../data/DemandTest.pdf')
    pdf_content2 = PDFDemand(
        title='Titulo de Ejemplo',
        description=data_text,
        urgency=5,
        user='Usuario Ejemplo',
        image=Path('imagen.jpg').absolute,
        category='Clases particulares',
        publication_date=datetime.now())
    print('PDF Generado en:')
    print(f2.write(pdf_content2))

    # FREELANCER
    f3 = PDFFile('../data/FreelancerTest.pdf')
    pdf_content3 = PDFFreelancer(
        username='Juanpe777',
        nombre='Juan Pérez',
        email='juanpe77@gmail.com',
        telefono='+34 123 456 789',
        posts={Offer('Title1', 'Ejdesc', 'User1'),
               Offer('Title2', 'Ejdesc', 'User2'),
               Offer('Title3', 'Ejdesc', 'User3')},
        habilidades=['Profesor', 'Ejemplo 2', 'Ejemplo 3'],
        opiniones=[8, 10, 7, 10],
        rating=7.5,
        money=122)
    print('PDF Generado en:')
    print(f3.write(pdf_content3))

    # Consumer
    f4 = PDFFile('../data/ConsumerTest.pdf')
    pdf_content4 = PDFConsumer(
        username='Juanpe777',
        nombre='Juan Pérez',
        email='juanpe77@gmail.com',
        telefono='+34 123 456 789',
        posts={Demand('Title1', 'Ejdesc', 'User1'),
               Demand('Title2', 'Ejdesc', 'User2'),
               Demand('Title3', 'Ejdesc', 'User3')},
        metodo_de_pago='Paypal',
        money=122,
        servicios_contratados={Offer('Title1', 'Ejdesc', 'User1'),
                               Offer('Title2', 'Ejdesc', 'User2'),
                               Offer('Title3', 'Ejdesc', 'User3')})
    print('PDF Generado en:')
    print(f4.write(pdf_content4))
