from pruebas import db
from offer import *
from demand import *

def fetch_posts_from_db(post_type: str = 'all', category: Optional[str] = None, keywords: Optional[list[str]] = None):
    """
    Loads posts from the database, applying filters based on type, category, and keywords.
    Returns a list of Offer or Demand Objects.

    Parameters
    ----------
    post_type : str
        'offer' for offers, 'demand' for demands, 'all' for both.
    category : str, optional
        Category to filter posts by.
    keywords : list of str, optional
        List of keywords to search for in title or description.

    Returns
    -------
    list of Post
        List of filtered Offer or Demand posts.
    """
    # Start with the base query
    query = """
    SELECT posts.id, users.username, posts.title, posts.description, posts.image, posts.date, posts.type 
    FROM posts
    JOIN users ON posts.user = users.id
    """

    # Add filtering by post type (offer or demand)
    if post_type == 'offer':
        query += " JOIN freelancers ON posts.user = freelancers.id"
    elif post_type == 'demand':
        query += " JOIN consumers ON posts.user = consumers.id"

    # Add filtering by category
    if category:
        query += f" JOIN post_categories ON posts.id = post_categories.post_id WHERE post_categories.category = '{category}'"

    # Add filtering by keywords in title or description
    if keywords:
        keyword_conditions = " OR ".join([f"posts.title LIKE '%{keyword}%'" for keyword in keywords] +
                                         [f"posts.description LIKE '%{keyword}%'" for keyword in keywords])
        if 'WHERE' in query:
            query += " AND (" + keyword_conditions + ")"
        else:
            query += " WHERE " + keyword_conditions

    # Execute the query
    success, cursor = db.query(query)

    if not success:
        print("❌ Error al obtener datos de la base de datos.")
        return []

    rows = cursor.fetchall()
    posts = []

    # Process the results into Offer or Demand objects
    for row in rows:
        post_id, username, title, description, image, date, post_type = row
        if post_type == 'offer':
            posts.append(Offer(title, description, username, image, price=0))  # Agregar precio según necesidad
        elif post_type == 'demand':
            posts.append(Demand(title, description, username, image, urgency=0))  # Agregar urgencia según necesidad

    return posts
