from unicodedata import category

from offer import *
from demand import *
from generic_posts import Post

# 🔹 Función para filtrar publicaciones según el tipo
def filter_posts(post_type = None, category = None, keywords = None):
    """
    Returns a filtered list of posts based on the selected type
    """

    # By type of post

    all_posts = list(Post.posts.values())

    if post_type == "offer":
        filtered = [post for post in all_posts if isinstance(post, Offer)]
    elif post_type == "demand":
        filtered = [post for post in all_posts if isinstance(post, Demand)]
    else:
        filtered = all_posts

    if category:
        filtered = [post for post in filtered if post.get_categories() == category]

    if keywords:
        filtered = [post for post in filtered if any(
            kw.lower() in post.title.lower() or kw.lower() in post.description.lower()
            for kw in keywords
        )]
