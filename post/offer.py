from typing import Optional, Self
from .generic_posts import Post
from file_utils import CSVFile, Path, PDFFile, PDFOffer
from db import Database, SixerrDB

def _init(_self: 'Offer', db: Database) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    type(_self).offer_feed[_self.title] = {"type": "offer", "description": _self.description,
                                         "user": _self.user, "price": _self.price, 'category': _self.category}

@Database.register(
    table='offer',
    map={'price':'price'},
    init=_init
)
class Offer(Post):
    """
    Class representing an offer, inheriting from Publication.

    Attributes
    ----------
    price : float
        Price associated with the offer.

    Methods
    -------
    display_information() -> str
        Displays the complete information of the offer.
    """
    offer_feed: dict[str,dict[str,str]] = {}
    def __init__(self, title: str, description: str, user: str, image: Optional[str]=None, price: float=0) -> None:
        """
        Initializes an Offer instance.

        Parameters
        ----------
        title : str
            Title of the offer.
        description : str
            Description of the offer.
        user : str
            User who publishes the offer.
        image : str, optional
            Image associated with the offer.
        price : float
            Price of the offer (default is 0).
        """
        super().__init__(title, description, user, image)
        self.price = price
        type(self).offer_feed[self.title] = {"type": "offer", "description": self.description,
                                             "user": self.user, "price": self.price, 'category': self.category}

    def add_category(self, category: str) -> None:
        """
        Adds a category to the offer, using super().add_category, also adds the category to 'offer_feed'.
        
        Parameters
        ----------
        category : str
            Category to be added.
        """
        super().add_category(category)
        type(self).offer_feed[self.title]['category'] = category

    @classmethod
    def import_post_csv(cls, path: str | Path) -> Self:
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
        Offer Instance
        """
        f = CSVFile(path)
        f.read()
        if f.data[0][-1] != 'Offer':
            raise NotImplementedError('Post type is not Offer')

        obj = cls.__new__(cls)
        for row in f.data:
            for i, value in enumerate(row):
                if f.headers[i] != 'post_type':
                    setattr(obj, f.headers[i], value)

        return obj


    def export_post_pdf(self, tempdir) -> str:
        f = PDFFile(f'{tempdir}/Post.pdf')
        pdf_content = PDFOffer(
            title=self.title,
            description=self.description,
            user=self.user,
            image=self.image,
            price=self.price,
            publication_date=self.publication_date,
            category=self.category
        )
        f.write(pdf_content)
        return f.path.absolute

    def display_information(self) -> str:
        """
        Displays the complete information of the offer, including the price.

        Returns
        -------
        str
            Detailed information about the offer.
        """
        base_info = super().display_information()
        return f'{base_info}\nPrice: {self.price}'