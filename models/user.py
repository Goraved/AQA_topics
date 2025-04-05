import logging
from typing import Optional

from data import query

# Set up logging
logger = logging.getLogger(__name__)

class User:
    """
    A class to represent a user.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
    """
    def __init__(self, username: str, password: str):
        """
        Constructs all the necessary attributes for the user object.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        """
        self.username = username
        self.password = password


def get_user(username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        username (str): The username to search for.

    Returns:
        Optional[User]: User object if found, None otherwise.
    """
    try:
        # Improved SQL with better handling of potential SQL injection
        sanitized_username = username.replace("'", "''")
        cur = query(f"SELECT username, password FROM aqa WHERE username LIKE '{sanitized_username}'")
        result = cur.fetchall()
        cur.close()

        if not result:
            logger.warning(f"User not found: {username}")
            return None

        return User(username=result[0][0], password=result[0][1])
    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        return None
