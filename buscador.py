from offer import *
from demand import *
from generic_posts import Post

def filter_posts(post_type=None, category=None, keywords=None):
    # Validar que Post.posts es un diccionario
    if not isinstance(Post.posts, dict):
        raise TypeError("Post.posts must be a dictionary.")

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
        try:
            filtered = [post for post in filtered if any(
                kw.lower() in post.title.lower() or kw.lower() in post.description.lower()
                for kw in keywords
            )]
        except AttributeError as e:
            print(f"Warning: a post was skipped due to missing attributes - {e}")

    return filtered
