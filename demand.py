from generic_posts import Post
from typing import Optional, Self
from file_utils import CSVFile, Path, PDFFile, PDFDemand, XMLFile


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

    @classmethod
    def import_post_xml(cls, path: str | Path) -> Self:
        f = XMLFile(path)
        obj = cls.__new__(cls)
        for key, value in f.read().items():
            if key == 'type' and value != 'Demand':
                raise NotImplementedError('Post type is not Demand')
            setattr(obj, key, value)

        return obj

    def export_post_pdf(self, tempdir) -> str:
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
