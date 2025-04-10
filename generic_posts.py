from abc import ABC, abstractmethod
from typing import Optional, Self
from datetime import datetime
from file_utils import CSVFile, Path
'''
@Database.register(
    table='posts',
    map={
        'user':'user',
        'title':'title',
        'fecha':'publication_date',
        'description':'description',
        'image':'image',
        'categories':'categories'
}
)
'''
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
    posts: dict[str, set] = {}

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
        self.publication_date = datetime.now().date()
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
            raise ValueError(f'The category "{category}" is not allowed')
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

    def export_post(self) -> Path:
        """
        Gets a post data and exports it to a CSV file

        Returns
        -------
        Path
            System path to the file
        """
        post_keys: list[str] = [key for key in self.__dict__.keys()]
        post_keys.append('post_type')
        post_values: list[str] = [value for value in self.__dict__.values()]
        file_name = f'{self.title}_{datetime.now().strftime("%Y%m%d")}.csv'
        f = CSVFile(f'data/{file_name}')
        if type(self).__name__ == 'Offer':
            post_values.append('Offer')
        elif type(self).__name__ == 'Demand':
            post_values.append('Demand')
        f.write_headers(post_keys)
        f.write(post_values)
        return f.path.absolute

    @classmethod
    @abstractmethod
    def import_post(cls, path: str | Path) -> Self:
        """
        Imports a post from a CSV file.  (Must be implemented in subclasses)

        To avoid unwanted behaviours CSV headers must be: (¡post_type must be last column!)
        title,description,user,image,publication_date,category,price/demand,post_type

        Parameters
        ----------
        path: str | Path
            Path to the CSV file.

        Returns
        -------
        Post Instance
        """
        pass

    @abstractmethod
    def display_information(self) -> str: # Usar __str__()
        """
        Abstract method to display the publication's information.

        Returns
        -------
        str
            Detailed information about the publication.
        """
        return f'Title: {self.title}, Description: {self.description}, Publication date: {self.publication_date}, User: {self.user}, Category: {self.category if self.category is not None else "No category"}'

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


