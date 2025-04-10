from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
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
    display_information() -> str
        Abstract method to be implemented by child classes.
    """


    allowed_categories = {
        "Mathematics", "Science", "Physics", "Chemistry", "Biology",
        "History", "Geography", "Literature", "Art", "Music",
        "Technology", "Computer Science", "Programming", "Robotics", "Astronomy",
        "Sports", "Health", "Philosophy", "Psychology", "Economics"
    }
    identification = 0
    posts: dict = {}

    #posts: dict[str, set] = {}

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
        Post.posts[Post.identification] = self
        Post.identification +=1

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

    @abstractmethod
    def display_information(self) -> str:
        """
        Abstract method to display the publication's information.

        Returns
        -------
        str
            Detailed information about the publication.
        """
        return f'Title: {self.title}, Description: {self.description}, Publication date: {self.publication_date}, User: {self.user}, Category: {self.category if self.category is not None else "No category"}'
