
from typing import Self
from .offer import Offer
from .demand import Demand
from file_utils import CSVFile, Path
from .exceptions import CorruptedFile

def import_post_csv(path: str | Path) -> Self:
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
    """
    Gets a post data and exports it to a CSV file

    Returns
    -------
    str
        Absolute System path to the file
    """
    f = CSVFile(path)

    if not f.read():
        raise CorruptedFile(path, 'CSV Unreadable')

    if f.headers[-1] != 'post_type':
        raise CorruptedFile(path, 'No post_type header')
    match f.data[-1]:
        case 'Offer':
            obj = Offer.__new__(Offer)
        case 'Demand':
            obj = Demand.__new__(Demand)
        case _:
            print(f.headers)
            print(f.data)
            raise CorruptedFile(path, 'Incorrect post_type value')
    for key, value in zip(f.headers[:-1], f.data[:-1]):
        obj.__dict__[key] = value

    return obj