from .generic_posts import Post
from typing import Optional, Self
from file_utils import CSVFile, Path, PDFFile, PDFDemand
from db import Database, SixerrDB

def _init(_self: 'Demand', db: Database) -> None:
    """
    Initializes the object instance when created externally

    In the process of external creation the object gets infused with data and outside initialized.
    """
    type(_self).demand_feed[_self.title] = {'type': 'demand', 'description': _self.description,
                                          'user': _self.user, 'urgency': _self.urgency, 'category': _self.category}

@Database.register(
    db=SixerrDB(),
    table='demand',
    map={'urgency':'urgency'},
    init=_init
)
class Demand(Post):
    """
    Class representing a demand, inheriting from Publication.

    Attributes
    ----------
    urgency : int
        Level of urgency associated with the demand. As higher is its value, higher is its urgency.

    Methods
    -------
    display_information() -> str
        Displays the complete information of the demand.
    """

    demand_feed: dict[str,dict[str,str]] = {}
    def __init__(self, title: str, description: str, user: str, image: Optional[str]=None, urgency: int=3) -> None:
        """
        Initializes a Demand instance.

        Parameters
        ----------
        title : str
            Title of the demand.
        description : str
            Description of the demand.
        user : str
            User who creates the demand.
        image : str, optional
            Image associated with the demand (default is None).
        urgency : int
            Level of urgency (e.g., from 1 to 5, where 5 is the highest urgency) (default is 3).
        """
        super().__init__(title, description, user, image)
        self.urgency = urgency
        type(self).demand_feed[self.title] = {'type': 'demand', 'description': self.description,
                                              'user': self.user, 'urgency': self.urgency, 'category': self.category}

    def add_category(self, category: str) -> None:
        """
        Adds a category to the demand.

        Parameters
        ----------
        category : str
            Category of the demand to be added.
        """
        super().add_category(category)
        type(self).demand_feed[self.title]['category'] = category

    @classmethod
    def import_post_csv(cls, path: str | Path) -> Self: # from_csv()
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
        Demand Instance
        """
        f = CSVFile(path)
        f.read()
        if f.data[0][-1] != 'Demand':
            raise NotImplementedError('Post type is not Demand')

        obj = cls.__new__(cls)
        for row in f.data:
            for i, value in enumerate(row):
                if f.headers[i] != 'post_type':
                    setattr(obj, f.headers[i], value)
        return obj

    def export_post_pdf(self, tempdir) -> str:
        """
        Gets all Demand's info and exports it into a PDF file.

        Parameters
        ----------
        tempdir: str
            Directory to save the PDF file.

        Returns
        -------
        str
            Absolute system path to a PDF file.
        """
        f = PDFFile(f'{tempdir}/Post.pdf')
        pdf_content = PDFDemand(
            title=self.title,
            description=self.description,
            user=self.user,
            image=self.image,
            urgency=self.urgency,
            publication_date=self.publication_date,
            category=self.category
        )
        f.write(pdf_content)
        return f.path.absolute


    def display_information(self) -> str:
        """
        Displays the complete information of the demand, including the urgency level.

        Returns
        -------
        str
            Detailed information about the demand.
        """
        base_info = super().display_information()
        return f'{base_info}, Urgency: {self.urgency}'
