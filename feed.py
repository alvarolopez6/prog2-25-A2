import time
import threading
from generic_posts import Post
from buscador import filter_posts

# Custom exceptions
class InvalidPostTypeError(Exception):
    def __str__(self):
        return "Error, post type has to be 'offer','demand' or 'all'. To neglect this filter press enter."

class InvalidCategoryError(Exception):
    def __str__(self):
        return "Sorry, that category does not exit yet. To neglect this filter press enter."

class InvalidKeywordsError(Exception):
    def __str__(self):
        return "Only letters, numbers and spaces are allowed in keywords. To neglect this filter, press Enter."

class InvalidFeedModeError(Exception):
    def __str__(self):
        return "Invalid mode. Choose 'auto' or 'manual'."

class NoMatchingPostsError(Exception):
    def __str__(self):
        return "No posts matched your search. Please try again with different filters."

class InvalidPostDataError(Exception):
    def __init__(self, post_id):
        self.post_id = post_id

    def __str__(self):
        return f"Post with ID {self.post_id} contains invalid or incomplete data."

def listen_keyboard(stop_feed):
    try:
        input("Press Enter anytime to stop the auto feed...")
        stop_feed[0] = True
    except Exception:
        print("There was a problem reading your input. The feed will continue.")

def show_auto_feed(posts):
    if not posts:
        print("No posts available.")
        return

    stop_feed = [False]
    keyboard_thread = threading.Thread(target=listen_keyboard, args=(stop_feed,))
    keyboard_thread.start()

    index = 0
    while not stop_feed[0]:
        try:
            print(posts[index].display_information())
        except Exception:
            print(InvalidPostDataError(post_id=posts[index].id))

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

def show_manual_feed(posts):
    if not posts:
        print("No posts available.")
        return

    index = 0
    while True:
        for i in range(index, index + 5):
            if 0 <= i < len(posts):
                try:
                    print(posts[i].display_information())
                except Exception:
                    print(InvalidPostDataError(post_id=posts[i].id))

        option = input("Press Enter to move forward | 'b' to go back | 'q' to exit: ").strip().lower()

        if option == "q":
            print("\nFeed closed.")
            break
        elif option == "b":
            if index >= 5:
                index -= 5
            else:
                print("No previous posts.")
        else:
            if index + 5 < len(posts):
                index += 5
            else:
                print("No more posts. Looping back to the start.")
                index = 0

if __name__ == '__main__':
    print('Posts can be filtered by type(offer/demand), category and keywords. These filters are applied independently. To neglect any filter press enter.')
    print('----------------------------')

    while True:
        while True:
            try:
                post_type = input(
                    "Choose post type to filer: 'offer' for Offers, 'demand' for Demands, 'all' for everything: ").strip().lower()

                if post_type == '':
                    post_type = 'all'
                    break
                elif post_type in ('offer','demand','all'):
                    break
                else:
                    raise InvalidPostTypeError()

            except (EOFError, KeyboardInterrupt):
                print("Input was interrupted. Please try again.")
                continue
            except InvalidPostTypeError as e:
                print(e)
                continue

        while True:
            try:
                category = input(
                    "Choose category to filter: ex. 'science', 'economics'...: ").strip().lower().capitalize()

                if category == '':
                    category = None
                    break
                elif category in Post.allowed_categories:
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
            filtered_posts = filter_posts(post_type, category, keywords)
            if not filtered_posts:
                raise NoMatchingPostsError()
        except NoMatchingPostsError as e:
            print(e)
            continue

        while True:
            try:
                print('There are 2 modes to see feed, automatic and manual. Automatic will display new posts every few seconds. Manual allows user to navigate freely through posts.')
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

        break
