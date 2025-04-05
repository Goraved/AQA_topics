import logging

from data import query, reformat_text

# Set up logging
logger = logging.getLogger(__name__)

class Category:
    """
    A class to represent a category.

    Attributes:
        name (str): The name of the category.
        icon (str): The icon associated with the category.
        category_id (int, optional): The ID of the category. Defaults to None.
        count (int): The number of topics in the category. Defaults to 0.
        index (int): The display order index of the category. Defaults to 0.
    """
    def __init__(self, name: str, icon: str, category_id: int = None):
        """
        Constructs all the necessary attributes for the category object.

        Args:
            name (str): The name of the category.
            icon (str): The icon associated with the category.
            category_id (int, optional): The ID of the category. Defaults to None.
        """
        self.name = name
        self.icon = icon
        self.category_id = category_id
        self.count = 0
        self.index = 0

    def create_category(self):
        """
        Creates a new category in the database with the current attributes.
        """
        query(f"INSERT INTO categories (title, icon) VALUES ('{reformat_text(self.name)}', '{self.icon}')")

    def update_category(self):
        """
        Updates the category in the database with the current attributes.
        """
        query(f"UPDATE categories SET title='{reformat_text(self.name)}', icon='{self.icon}'"
              f" WHERE id = {self.category_id}")

    @staticmethod
    def remove_category(category_id: int):
        """
        Removes a category from the database.

        Args:
            category_id (int): The ID of the category to be removed.
        """
        query(f"DELETE FROM categories WHERE id = {category_id}")


async def get_categories() -> list[Category]:
    """
    Asynchronous function to get all categories from the database.

    Returns:
        list[Category]: A list of Category objects representing the categories.
    """
    categories = []
    try:
        cur = query("SELECT id, title, icon FROM categories")
        for row in cur.fetchall():
            categories.append(Category(
                category_id=row[0],
                name=row[1],
                icon=row[2] if len(row) > 2 else 'fa-question-circle'  # Default icon if missing
            ))
        cur.close()
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
    return categories


def count_of_topic_in_cat(categories: list[Category], topics):
    """
    Count the number of topics in each category and set index for display ordering.

    This uses a more efficient counting approach with a single pass through the topics.

    Args:
        categories (list[Category]): A list of Category objects to be updated with topic counts.
        topics (list): A list of topics to be counted.
    """
    # Initialize counts
    category_counts = {category.category_id: 0 for category in categories}

    # Count topics per category
    for topic in topics:
        if topic.category_id in category_counts:
            category_counts[topic.category_id] += 1

    # Update category objects
    index = 0
    for category in categories:
        count = category_counts.get(category.category_id, 0)
        category.count = count

        # Set index for non-empty categories (except category_id 4)
        if category.category_id != 4 and count > 0:
            category.index = index
            index += 1