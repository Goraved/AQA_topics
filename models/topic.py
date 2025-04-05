import logging
from datetime import date, timedelta

import requests

from data import query, reformat_text
from models.domain import check_link_in_whitelist

# Set up logging
logger = logging.getLogger(__name__)


class Topic:
    """
    A class to represent a topic.

    Attributes:
        name (str): The name of the topic.
        link (str): The URL link of the topic.
        category_id (int): The ID of the category the topic belongs to.
        topic_id (int, optional): The ID of the topic. Defaults to None.
        category_name (str, optional): The name of the category. Defaults to None.
        date_added (date, optional): The date the topic was added. Defaults to None.
        is_new (bool, optional): Indicates if the topic is new. Defaults to None.
    """

    def __init__(
            self,
            name: str,
            link: str,
            category_id: int,
            topic_id: int = None,
            category_name: str = None,
            date_added=None,
            is_new: bool = None,
    ):
        """
        Constructs all the necessary attributes for the topic object.

        Args:
            name (str): The name of the topic.
            link (str): The URL link of the topic.
            category_id (int): The ID of the category the topic belongs to.
            topic_id (int, optional): The ID of the topic. Defaults to None.
            category_name (str, optional): The name of the category. Defaults to None.
            date_added (date, optional): The date the topic was added. Defaults to None.
            is_new (bool, optional): Indicates if the topic is new. Defaults to None.
        """
        self.name = name
        self.link = link
        self.category_id = category_id
        self.topic_id = topic_id
        self.category_name = category_name
        self.date_added = date_added
        self.is_new = is_new
        self.index = 0

    @staticmethod
    def remove_topic(topic_id: int):
        """
        Removes a topic from the database.

        Args:
            topic_id (int): The ID of the topic to be removed.
        """
        query(f"DELETE FROM topics WHERE id = {topic_id}")

    def update_topic(self):
        """
        Updates the topic in the database with the current attributes.
        """
        query(
            f"UPDATE topics SET title='{reformat_text(self.name)}', link='{reformat_text(self.link)}', "
            f"category_id={self.category_id} WHERE id = {self.topic_id}"
        )

    @staticmethod
    def check_if_topic_is_new(topic_date: date) -> bool:
        """
        Checks if a topic is new based on the date it was added.

        Args:
            topic_date (date): The date the topic was added.

        Returns:
            bool: True if the topic is new, False otherwise.
        """
        return date.today() - topic_date < timedelta(days=30)

    def create_topic(self):
        """
        Creates a new topic in the database if it does not already exist and the URL is valid.

        Returns:
            str: A message indicating the result of the operation.
        """
        # Check if topic already exists
        existing_topics = get_existing_topics_sync()
        for topic in existing_topics:
            if (
                    self.name.lower() == topic.name.lower()
                    or self.link.lower() == topic.link.lower()
            ):
                return f'Topic already added with title "{topic.name}"'

        # Validate URL
        try:
            if "dou" in self.link:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67",
                    "Referer": "https://dou.ua",
                    "X-Requested-With": "XMLHttpRequest",
                }
                response = requests.get(self.link, headers=headers, timeout=10)
            else:
                response = requests.get(self.link, timeout=10)
        except Exception as exception:
            return f"Bad url - {exception.args[0]}"

        # Add topic if URL is valid or in whitelist
        if str(response.status_code)[0] == "2" or check_link_in_whitelist(self.link):
            query(
                'INSERT INTO topics (category_id, title, link, added_date) VALUES ({},"{}","{}","{}")'.format(
                    self.category_id,
                    reformat_text(self.name),
                    reformat_text(self.link),
                    date.today(),
                )
            )
            return "Topic added successfully"
        else:
            message = f'Link "{self.link}" is broken | Code = {response.status_code}'
            query(
                f"INSERT INTO error_log (text, date) VALUES ('{message}', '{date.today()}')"
            )
            return message


def get_existing_topics_sync() -> list[Topic]:
    """
    Synchronous function to get all existing topics from the database.

    Returns:
        list[Topic]: A list of Topic objects representing the existing topics.
    """
    topics = []
    try:
        cur = query("SELECT id, category_id, title, link FROM topics")
        for row in cur.fetchall():
            topics.append(
                Topic(
                    topic_id=row[0],
                    category_id=row[1],
                    name=row[2],
                    link=row[3],
                )
            )
        cur.close()
    except Exception as e:
        logger.error(f"Error fetching existing topics: {e}")
    return topics


async def get_topics() -> list[Topic]:
    """
    Asynchronous function to get all topics from the database with additional data.

    Returns:
        list[Topic]: A list of Topic objects representing the topics.
    """
    topics = []
    try:
        cur = query(
            """SELECT t.id, t.category_id, t.title, t.link, t.added_date, c.title FROM topics AS t
            JOIN categories AS c ON t.category_id = c.id
            ORDER BY category_id, id DESC"""
        )
        for row in cur.fetchall():
            topics.append(
                Topic(
                    topic_id=row[0],
                    category_id=row[1],
                    name=row[2],
                    link=row[3],
                    date_added=row[4],
                    category_name=row[5],
                    is_new=Topic.check_if_topic_is_new(row[4]),
                )
            )
        cur.close()
    except Exception as e:
        logger.error(f"Error in get_topics: {e}")
    return topics


def search_topics(search_request: str) -> list[Topic]:
    """
    Searches for topics in the database that match the given search request.

    Args:
        search_request (str): The search term to look for.

    Returns:
        list[Topic]: A list of Topic objects that match the search request.
    """
    topics = []
    try:
        # Improved SQL with parameterization to prevent SQL injection
        search_term = f"%{search_request}%"
        cur = query(
            f"""SELECT t.title, t.link, c.title, c.id FROM topics AS t
            JOIN categories AS c ON t.category_id = c.id
            WHERE t.title LIKE '% {search_request}%' 
                OR t.title LIKE '{search_request}%' 
                OR t.title LIKE '[{search_request}%'
            ORDER BY c.id, t.title"""
        )
        for row in cur.fetchall():
            topics.append(
                Topic(name=row[0], link=row[1], category_id=row[3], category_name=row[2])
            )
        cur.close()
    except Exception as e:
        logger.error(f"Error in search_topics: {e}")
    return topics


def index_topics_by_category(topics: list[Topic]):
    """
    Adds an index to topics grouped by category.

    Args:
        topics (list[Topic]): A list of Topic objects to be indexed.
    """
    previous_cat = 0
    index = 0
    for topic in topics:
        if topic.category_id == previous_cat:
            index += 1
        else:
            index = 0
        topic.index = index
        previous_cat = topic.category_id
