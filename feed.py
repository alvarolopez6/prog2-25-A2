import time
import threading
from pruebas import db
from generic_posts import allowed_categories
from offer import *
from demand import *
from buscador import fetch_posts_from_db

def listen_keyboard(stop_feed):
    """
        Waits for the user to press Enter to stop the auto feed.

        Parameters
        ----------
        stop_feed : list of bool
            List containing a boolean value that indicates whether the feed should stop.

        Returns
        -------
        None
        """
    input("🔽 Press Enter anytime to stop the auto feed...")
    stop_feed[0] = True
    print("\n🚀 Feed stopped by user!")

def show_auto_feed(posts):
    """
        Continuously displays filtered posts in a circular motion
        until the user stops it.

        Parameters
        ----------
        posts : list of Post
            List of posts to be displayed in the feed.

        Returns
        -------
        None
        """

    if not posts:
        print("No posts available.")
        return

    # Start the thread to listen for keyboard input
    stop_feed = [False]
    keyboard_thread = threading.Thread(target=listen_keyboard, args=(stop_feed,))
    keyboard_thread.start()

    index = 0
    while not stop_feed[0]:
        print(posts[index].display_information())

        # 3 second timer between posts
        for _ in range(3): # Uses a loop to wait for 3 seconds
            if stop_feed[0]: # check every second for stop input
                keyboard_thread.join()
                return
            time.sleep(1)

        index += 1
        if index >= len(posts):
            index = 0

    keyboard_thread.join() # wait for thread to end
    print("\n🚀 Feed stopped by user!")


def show_manual_feed(posts):
    """
        Displays posts in manual mode with navigation options.

        Parameters
        ----------
        posts : list of Post
            List of posts to be displayed in the feed.

        Returns
        -------
        None
        """
    if not posts:
        print("No posts available.")
        return

    index = 0
    while True:
        for i in range(index, index + 5):
            if 0 <= i < len(posts):
                print(posts[i].display_information())

        option = input("🔹 Press Enter to move forward | 'b' to go back | 'q' to exit: ").strip().lower()

        if option == "q": # Exit feed
            print("\n🚀 Feed closed!")
            break
        elif option == "b": # Previous posts
            if index >= 5:
                index -= 5
            else:
                print("⛔ No previous posts.")
        else: # Next posts
            if index + 5 < len(posts):
                index += 5
            else:
                print('⛔ No more posts. Looping back to the start.')
                index = 0


if __name__ == '__main__':
    # Select post type
    while True:
        post_type = input(
            "Choose post type to filer: 'offer' for Offers, 'demand' for Demands, 'all' for everything: ").strip().lower()
        if post_type in ('offer','demand','all'):
                break
        else:
            print("Error, post type has to be 'offer','demand' or 'all'")

    # Select category of post
    while True:
        category = input(
            "Choose category to filter: ex. 'science', 'economics'...: ").strip().lower()
        if category in allowed_categories:
            break
        else:
            print("Sorry, that category does not exit yet")

    # Enter keywords for search
    keywords = input(
        "Introduce keywords to search for: no comas, just words separates with a space:").split()
    filtered_posts = fetch_posts_from_db(post_type, category, keywords)

    # Select feed mode
    while True:
        mode = input("Choose feed mode: 'auto' for automatic, 'manual' for manual: ").strip().lower()
        if mode == "auto":
            show_auto_feed(filtered_posts)
            break
        elif mode == "manual":
            show_manual_feed(filtered_posts)
            break
        else:
            print("Invalid mode. Choose 'auto' or 'manual'.")
