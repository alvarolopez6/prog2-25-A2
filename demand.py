from generic_posts import *
from typing import Optional

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

    def __init__(self, title: str, description: str, user: str, image: Optional[str], urgency: int) -> None:
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
            Level of urgency (e.g., from 1 to 5, where 5 is the highest urgency).
        """
        super().__init__(title, description, user, image)
        self.urgency = urgency

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
