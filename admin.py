from user import User
from generic_posts import Post

class Admin(User):
    """
    Class that represent an Admin user.
    Admin users have privileges to delete any post or user

    Attributes
    ----------
    username: str
        an unique string used to identify objects from others
    nombre: str
        the name of the user
    password: str
        an unique code that allows you to access to a certain account
    email: str
        a string which provides more information about emails of users
    telefono: int
        an int that represents the phone number of users
    fecha_creacion: str
        an date that provides information about the time of the creation of certain account

    Methods
    -------
    delete_user(username: str) -> None
        Deletes an user by their username

    delete_post(post_name: str) -> None
        Deletes a post by its name

    """
    def __init__(self, username: str, nombre: str, password: str, email: str, telefono: str =None) -> None:
        """
           Initializes an User instance

           Parameters
           ----------
           username: str
                an unique string used to identify objects from others
           nombre: str
                the name of the user
           password: str
                an unique code that allows you to access to a certain account (hash system)
           email: str
                a string which provides more information about emails of users
           telefono: int
                an int that represents the phone number of users
            """
        super().__init__(username, nombre, password, email, telefono)

    @staticmethod
    def delete_user(username: str) -> None:
        """
        Deletes an user by their username

        Parameters
        ----------
        username: str
            String with the username to be deleted
        """
        User.usuarios.pop(username)

    @staticmethod
    def delete_post(post_name: str) -> None:
        """
        Deletes a post by their name

        Parameters
        ----------
        post_name: str
            String with the name of the post to be deleted
        """
        for post in Post.post_set:
            if post.title == post_name:
                del post