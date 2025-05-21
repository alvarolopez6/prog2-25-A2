from unicodedata import category

from offer import *
from demand import *
from generic_posts import Post

def filter_posts(post_type = None, category = None, keywords = None):
    """
            Filters the posts based on post type, category, and keywords.

            Parameters
            ----------
            post_type : str or None
                Type of post to filter ('offer', 'demand', or None for all).
            category : str or None
                Specific category to filter posts by.
            keywords : list of str or None
                List of keywords to search within title and description.

            Returns
            -------
            list of Post
                A list of posts that match the applied filters.
        """

    # Get all posts from the shared Post class storage
    all_posts = list(Post.posts.values())

    # Filter by post type
    if post_type == "offer":
        filtered = [post for post in all_posts if isinstance(post, Offer)]
    elif post_type == "demand":
        filtered = [post for post in all_posts if isinstance(post, Demand)]
    else:
        filtered = all_posts

    # Filter by category (if provided)
    if category:
        filtered = [post for post in filtered if post.get_category() == category]

    # Filter by keywords (if provided)
    if keywords:
        filtered = [post for post in filtered if any(
            kw.lower() in post.title.lower() or kw.lower() in post.description.lower()
            for kw in keywords
        )]
    return filtered