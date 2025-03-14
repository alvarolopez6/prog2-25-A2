from generic_posts import *
from typing import Optional

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

    def __init__(self, title: str, description: str, user: str,
                 image: Optional[str], price: float, publication_date: str = datetime.now().date()) -> None:
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
            Price of the offer.
        """
        super().__init__(title, description, user, image)
        self.price = price

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
