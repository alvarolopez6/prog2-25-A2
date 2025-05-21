import time
import threading
from generic_posts import Post
from buscador import filter_posts

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
        print()
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
    print('Posts can be filtered by type(offer/demand), category and keywords. These filteres are applied independently. To neglect any filter press enter')
    print('----------------------------')
    while True:
        post_type = input(
            "Choose post type to filer: 'offer' for Offers, 'demand' for Demands, 'all' for everything: ").strip().lower()
        if post_type == '':
            post_type = 'all'
            break
        elif post_type in ('offer','demand','all'):
            break
        else:
            print("Error, post type has to be 'offer','demand' or 'all'. To neglect this filter press enter")

    # Select category of post
    while True:
        category = input(
            "Choose category to filter: ex. 'science', 'economics', etc.: ").strip().lower().capitalize()
        if category == '':
            category = None
            break
        elif category in Post.allowed_categories:
            break
        else:
            print("Sorry, that category does not exit yet. To neglect this filter press enter")

    # Enter keywords for search
    while True:
        keywords = input(
            "Choose keywords to search for: try something like 'english teacher' or 'logo design':")
        if keywords == '':
            keywords = None
        elif all(c.isalnum() or c.isspace() for c in keywords):
            keywords = [word.lower() for word in keywords.split()]
        else:
            print("To apply a keyword filter only numbers, letters and spaces are allowed. To neglect this filter press enter")
        break

    filtered_posts = filter_posts(post_type, category, keywords)

    # Select feed mode
    while True:
        print('There is 2 modes to see feed, automatic and manual. Automatic will display new posts every few seconds. Manual allows user to navigate freely through posts')
        mode = input("Choose feed mode: 'auto' for automatic, 'manual' for manual: ")
        if mode == "auto":
            show_auto_feed(filtered_posts)
            break
        elif mode == "manual":
            show_manual_feed(filtered_posts)
            break
        else:
            print("Invalid mode. Choose 'auto' or 'manual'.")
