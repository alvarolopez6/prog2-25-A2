from typing import Optional, Self
from generic_posts import Post
from file_utils import CSVFile, Path, PDFFile, PDFOffer

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

    @classmethod
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
        return f'{base_info}, Price: {self.price}'
