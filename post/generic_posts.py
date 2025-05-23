from abc import ABC, abstractmethod
from typing import Optional, Self
from datetime import datetime
from file_utils import CSVFile, Path, XMLFile
from db import Database, SixerrDB
import multiprocessing as mp
import tempfile
import zipfile

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except ImportError:
    compression = zipfile.ZIP_STORED

modes = {zipfile.ZIP_DEFLATED: 'deflated', zipfile.ZIP_STORED: 'stored'}



def _init(_self: 'Post', db: Database) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    if _self.user in Post.posts:
        Post.posts[_self.user].add(_self)
    else:
        Post.posts[_self.user] = {_self}


@Database.register(
    db=SixerrDB(),
    table='posts',
    map={
        'username':'user',
        'title':'title',
        'fecha':'publication_date',
        'description':'description',
        'image':'image',
        'category':'category'
    }, init=_init
)
class Post(ABC):
    """
    Abstract class representing a generic publication.

    Attributes
    ----------
    allowed_categories : set
        Set of allowed categories for the publication.
    identification: int
        Unique number of identification for each post.
    posts: dict
        Dictionary where all the posts get saved.
    title : str
        Title of the publication.
    description : str
        Description of the publication.
    user : str
        User who creates the publication.
    image : str, optional
        URL or path to the associated image (default is None).
    publication_date : datetime.date
        Date when the content is published (default is the current date).
    category : str
        Category associated with the publication.

    Methods
    -------
    add_category(category: str) -> None
        Adds a category if it is in the allowed categories list.
    remove_category(category: str) -> None
        Removes a category if it exists.
    get_category() -> str
        Returns the associated category of a post.
    export_post() -> Path
        Exports all post's information into a CSV file
    import_post() -> Self
        Imports a post from a CSV file. (Must be implemented in subclasses)
    display_information() -> str
        Abstract method to be implemented by child classes.
    get_post() -> Self | None
        Returns a post instance by its title and publisher username
    """

    allowed_categories = {
        "Mathematics", "Science", "Physics", "Chemistry", "Biology",
        "History", "Geography", "Literature", "Art", "Music",
        "Technology", "Computer Science", "Programming", "Robotics", "Astronomy",
        "Sports", "Health", "Philosophy", "Psychology", "Economics"
    }
    posts: dict[str, set[Self]] = {}

    def __init__(self, title: str, description: str, user: str, image: Optional[str] = None) -> None:
        """
        Initializes a Publication instance.

        Parameters
        ----------
        title : str
            Title of the publication.
        description : str
            Description of the publication.
        user : str
            User who publishes the content.
        image : str, optional
            Image associated with the publication (default is None).
        """
        self.title = title
        self.description = description
        self.user = user
        self.image = image
        self.publication_date = datetime.now().date().strftime('%Y/%m/%d')
        self.category = None

        if user in Post.posts:
            Post.posts[user].add(self)
        else:
            Post.posts[user] = {self}


    def add_category(self, category: str) -> None:
        """
        Adds a category to the publication if it is in the allowed categories list.

        Parameters
        ----------
        category : str
            The name of the category to add.

        Notes
        -----
        If the category is not in `allowed_categories`, an error message is displayed.
        """
        if category not in self.allowed_categories:
            raise ValueError(f'La categoria "{category}" no esta permitida')
        self.category = category

    def remove_category(self) -> None:
        """
        Removes a category from the publication if it exists.
        """
        self.category = None

    def get_category(self) -> str:
        """
        Returns the associated category of a post.

        Returns
        -------
        str
            Associated category.
        """
        return self.category

    def export_post_csv(self, tempdir) -> str:
        """
        Gets a post data and exports it to a CSV file

        Returns
        -------
        str
            Absolute System path to the file
        """
        post_keys: list[str] = [key for key in self.__dict__.keys()]
        post_keys.append('post_type')
        post_values: list[str] = [value for value in self.__dict__.values()]
        f = CSVFile(f'{tempdir}/Post.csv')
        if type(self).__name__ == 'Offer':
            post_values.append('Offer')
        elif type(self).__name__ == 'Demand':
            post_values.append('Demand')
        f.write_headers(post_keys)
        f.write(post_values)
        return f.path.absolute

    @abstractmethod
    def export_post_pdf(self, tempdir) -> str:
        """
        Gets a post data and exports it to a PDF file. (Must be implemented in subclasses)

        Returns
        -------
        str
            Absolute System path to the file
        """
        pass

    def export_post_xml(self, tempdir) -> str:
        """
        Gets post's data and exports it to a XML file.

        Returns
        -------
        str
            Absolute System path to the file
        """
        f = XMLFile(f'{tempdir}/Post.xml')
        f.gen_tree('SixerrData')
        data_dict = {'type': type(self).__name__, **self.__dict__,
                     'publication_date': self.publication_date}
        f.write(data_dict)
        f.indent()
        return f.path.absolute

    def export_post(self) -> str:
        """
        Gets a post data and exports it to a ZIP file with a .csv, .pdf, and .xml files inside.

        Returns
        -------
        str
            Absolute System path to the file
        """
        funcs = [self.export_post_csv, self.export_post_pdf, self.export_post_xml]
        proccess: list[mp.Process] = []

        temp_dir = 'data/'

        for f in funcs:
            p = mp.Process(target=f, args=(temp_dir,))
            proccess.append(p)
            p.start()

        for p in proccess:
            p.join()

        file_name = f'{self.title}_{datetime.now().strftime("%Y%m%d")}.zip'
        zip_file = Path(f'{temp_dir}/{file_name}')

        with zipfile.ZipFile(zip_file.absolute, 'w') as z:
            z.write(Path(f'{temp_dir}/Post.csv').absolute, self.title + '.csv', compress_type=compression)
            z.write(Path(f'{temp_dir}/Post.pdf').absolute, self.title + '.pdf', compress_type=compression)
            z.write(Path(f'{temp_dir}/Post.xml').absolute, self.title + '.xml', compress_type=compression)

        return zip_file.absolute

    @abstractmethod
    def display_information(self) -> str:
        """
        Abstract method to display the publication's information.

        Returns
        -------
        str
            Detailed information about the publication.
        """
        return (f'Title: {self.title}\nDescription: {self.description}'
                f'\nPublication date: {self.publication_date}\nUser: {self.user}'
                f'\nCategory: {self.category if self.category else "No category"}')

    @classmethod
    def get_post(cls, user: str, title: str) -> Self | None:
        """
        Returns a post by its user and title.

        Parameters
        ----------
        user: str
            Username who published the post.
        title: str
            Title of the post.

        Returns
        -------
        Self | None
            Post instance if it exists, None otherwise.
        """
        encontrado=False
        if user in cls.posts:
            for post in cls.posts[user]:
                if post.title == title:
                    encontrado=True
                    return post
            if not encontrado:
                raise ValueError("El titulo no esta en nuestra base de datos")


