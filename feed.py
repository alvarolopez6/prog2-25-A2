import time
import threading
from typing import Any, Optional

# Set of allowed categories to validate user input for category filters
allowed_categories = {
        "Mathematics", "Science", "Physics", "Chemistry", "Biology",
        "History", "Geography", "Literature", "Art", "Music",
        "Technology", "Computer Science", "Programming", "Robotics", "Astronomy",
        "Sports", "Health", "Philosophy", "Psychology", "Economics"
    }

# Custom exceptions
class InvalidPostTypeError(Exception):
    """
    Exception raised when an invalid post type is passed.
    """
    def __str__(self) -> str:
        return "Error, post type has to be 'offer','demand' or 'all'. To neglect this filter press enter."


class InvalidCategoryError(Exception):
    """
    Exception raised when an invalid category is passed.
    """
    def __str__(self) -> str:
        return "Sorry, that category does not exit yet. To neglect this filter press enter."


class InvalidKeywordsError(Exception):
    """
    Exception raised when invalid keywords are passed.
    """
    def __str__(self) -> str:
        return "Only letters, numbers and spaces are allowed in keywords. To neglect this filter, press Enter."


class InvalidFeedModeError(Exception):
    """
    Exception raised when an invalid feed mode is passed.
    """
    def __str__(self) -> str:
        return "Invalid mode. Choose 'auto' or 'manual'."


class NoMatchingPostsError(Exception):
    """
    Exception raised when no posts match the given criteria.
    """
    def __str__(self) -> str:
        return "No posts matched your search. Please try again with different filters."


def display_information(info: tuple[str, dict[str, Any]]) -> str:
    """
    Displays information about the given post.

    Parameters
    ----------
    info : tuple[str, dict[str, Any]]
        Post information. (title, {description:, ...})

    Returns
    -------
    str
        String representation of the post.
    """
    return (f"Titulo:{info[0]}\nDescripción:{info[1]['description']}\nCreado por: {info[1]['user']}\n" +
            (f"Urgencia: {info[1]['urgency']}" if info[1]['type'] == 'demand'
            else f"Precio: {info[1]['price']}€"))

def filter_posts(post_type: Optional[str] = None,
                 category: Optional[str] = None, keywords: Optional[str] = None,
                 post_dict: dict[str, dict[str, Any]]=None) -> list[tuple[str, dict[str, Any]]]:
    """
    Filters posts given, using a given criteria.

    Parameters
    ----------
    post_type : str, optional
        Post type to filter. Defaults to all posts.
    category : str, optional
        Category to filter. Defaults to all categories.
    keywords : str, optional
        Keywords to filter. Defaults to None.
    post_dict : dict[str, dict[str, Any]]
        Dict with all posts. Title is key, other information is the value.

    Returns
    -------
    list[tuple[str, dict[str, Any]]]
        Filtered posts.
    """
    # Validar que post_dict es un diccionario
    if not isinstance(post_dict, dict):
        raise TypeError("Post.posts must be a dictionary.")

    if post_type == "offer":
        filtered = [(title, info)
                    for title, info in post_dict.items() if post_dict[title]['type'] == 'offer']
    elif post_type == "demand":
        filtered = [(title, info)
                    for title, info in post_dict.items() if post_dict[title]['type'] == 'demand']
    else:
        filtered = [(title, info) for title, info in post_dict.items()]

    if category:
        filtered = [(title, info) for title, info in filtered if info['category'] == category]

    if keywords:
        try:
            filtered = [(title, info) for title, info in filtered if any(
                kw.lower() in title.lower() or kw.lower() in info['description'].lower()
                for kw in keywords
            )]
        except AttributeError as e:
            print(f"Warning: a post was skipped due to missing attributes - {e}")

    return filtered

def listen_keyboard(stop_feed: list[bool]) -> None:
    """
    Waits for user to press Enter to stop the automatic feed.

    Parameters
    ----------
    stop_feed : list[bool]
        Shared list used as a flag to stop the feed.
    """
    try:
        input("Press Enter anytime to stop the auto feed...\n")
        stop_feed[0] = True
    except Exception:
        print("There was a problem reading your input. The feed will continue.")

def show_auto_feed(posts: list[tuple[str, dict[str, Any]]]) -> None:
    """
    Displays posts automatically every few seconds until interrupted by the user.

    Parameters
    ----------
    posts : list[tuple[str, dict[str, Any]]]
        List of posts to be shown.
    """
    if not posts:
        print("No posts available.")
        return

    stop_feed = [False]
    keyboard_thread = threading.Thread(target=listen_keyboard, args=(stop_feed,))
    keyboard_thread.start()

    index = 0
    while not stop_feed[0]:
        print(display_information(posts[index]))
        print()
        for _ in range(3):
            if stop_feed[0]:
                keyboard_thread.join()
                return
            time.sleep(1)

        index += 1
        if index >= len(posts):
            index = 0

    keyboard_thread.join()
    print("\nFeed stopped by user.")

def show_manual_feed(posts: list[tuple[str, dict[str, Any]]]) -> None:
    """
    Allows user to manually navigate through the list of posts.

    Parameters
    ----------
    posts : list[tuple[str, dict[str, Any]]]
        List of posts to be shown.
    """
    if not posts:
        print("No posts available.")
        return

    index = 0
    while True:
        print(display_information(posts[index]))

        option = input("Press Enter to move forward | 'b' to go back | 'q' to exit: ").strip().lower()

        if option == "q":
            print("\nFeed closed.")
            break
        elif option == "b":
            if index > 0:
                index -= 1
            else:
                print("No previous posts.")
        else:
            if index < len(posts) - 1:
                index += 1
            else:
                print("No more posts. Looping back to the start.")
                index = 0

def feed(post_dict: list[tuple[str, dict[str, Any]]]) -> None:
    """
    Main function to execute the feed, ask for filters and display posts accordingly.

    Parameters
    ----------
    post_dict : dict[str, dict[str, Any]]
        Dictionary of posts to be processed.
    """
    print(
        'Posts can be filtered by type(offer/demand), category and keywords. These filters are applied independently. '
        'To neglect any filter press enter.')
    print('-' * 75)

    closefeed = False
    while not closefeed:
        while True:
            try:
                print("Type: 'c' to close feed")
                post_type = input(
                    "Choose post type to filer: 'offer' for Offers, 'demand' for Demands: ").strip().lower()

                if post_type == '':
                    post_type = 'all'
                    break
                elif post_type in ('offer', 'demand', 'all'):
                    break
                elif post_type == 'c':
                    closefeed = True
                    break
                else:
                    raise InvalidPostTypeError()

            except (EOFError, KeyboardInterrupt):
                print("Input was interrupted. Please try again.")
                continue
            except InvalidPostTypeError as e:
                print(e)
                continue
        if closefeed:
            print("Closing feed...\n")
            break

        while True:
            try:
                category = input(
                    "Choose category to filter: ex. 'science', 'economics'...: ").strip().lower().capitalize()

                if category == '':
                    category = None
                    break
                elif category in allowed_categories:
                    break
                else:
                    raise InvalidCategoryError()

            except (EOFError, KeyboardInterrupt):
                print("Input was interrupted. Please try again.")
                continue
            except InvalidCategoryError as e:
                print(e)
                continue

        while True:
            try:
                keywords = input("Choose keywords to search for: try something like 'english teacher' or 'logo design'")

                if keywords == '':
                    keywords = None
                    break
                elif all(c.isalnum() or c.isspace() for c in keywords):
                    keywords = keywords.lower().split()
                    break
                else:
                    raise InvalidKeywordsError()

            except (EOFError, KeyboardInterrupt):
                print("Input was interrupted. Please try again.")
                continue
            except InvalidKeywordsError as e:
                print(e)
                continue

        try:
            filtered_posts = filter_posts(post_type, category, keywords, post_dict)
            if not filtered_posts:
                raise NoMatchingPostsError()
        except NoMatchingPostsError as e:
            print(e)
            continue

        while True:
            try:
                print(
                    'There are 2 modes to see feed, automatic and manual. Automatic will display new posts every few seconds. Manual allows user to navigate freely through posts.')
                mode = input("Choose feed mode: 'auto' for automatic, 'manual' for manual: ").strip().lower()

                if mode == "auto":
                    show_auto_feed(filtered_posts)
                    break
                elif mode == "manual":
                    show_manual_feed(filtered_posts)
                    break
                else:
                    raise InvalidFeedModeError()

            except (EOFError, KeyboardInterrupt):
                print("Input was interrupted. Please try again.")
                continue
            except InvalidFeedModeError as e:
                print(e)
                continue

if __name__ == '__main__':
    diccionario = {'Titulo1': {'type': 'offer', 'description': 'descripcionejemplo', 'user': 'younes', 'price': 15.99},
                   'Titulo2': {'type': 'demand', 'description': 'descripcion22ejemplo', 'user': 'llunes', 'urgency': 5},
                   'Titulo3': {'type': 'offer', 'description': 'descripcion333ejemplo', 'user': 'younes', 'price': 15.99},
                   'Titulo4': {'type': 'offer', 'description': 'descripcion4444ejemplo', 'user': 'younes', 'price': 15.99}}
    feed(diccionario)