import os
from datetime import date

from mysql import connector
from mysql.connector.cursor import MySQLCursor

# Global database connection
DB = None

def db_connection():
    """
    Establishes a connection to the MySQL database using credentials from environment variables.
    Sets the global DB variable to the connection object.
    """
    global DB
    DB = connector.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_HOST"],
        database=os.environ["DB"],
        connect_timeout=6000,
    )
    DB.ping(True)

def close_connection():
    """
    Closes the MySQL database connection if it is open.
    Sets the global DB variable to None.
    """
    global DB
    if DB:
        DB.close()

def query(sql: str) -> MySQLCursor:
    """
    Executes a given SQL query on the MySQL database.
    Reconnects to the database if the connection is lost.

    Args:
        sql (str): The SQL query to be executed.

    Returns:
        MySQLCursor: The cursor object containing the results of the query.
    """
    global DB
    if not DB:
        db_connection()

    try:
        cursor = DB.cursor(buffered=True)
        cursor.execute(sql)
        DB.commit()
    except:
        db_connection()
        DB.ping(True)
        cursor = DB.cursor()
        cursor.execute(sql)
        DB.commit()
    return cursor

def reformat_text(text: str) -> str:
    """
    Reformats a given text by stripping leading and trailing whitespace and removing angle brackets.

    Args:
        text (str): The text to be reformatted.

    Returns:
        str: The reformatted text.
    """
    return str(text).strip().replace("<", "").replace(">", "")

async def get_season() -> str:
    """
    Determines the current season based on the current month.

    Returns:
        str: The current season ("winter", "spring", "summer", or "autumn").

    Raises:
        Exception: If the current month is not within the expected range.
    """
    current_month = date.today().month
    if current_month in [12, 1, 2]:
        season = "winter"
    elif current_month in [3, 4, 5]:
        season = "spring"
    elif current_month in [6, 7, 8]:
        season = "summer"
    elif current_month in [9, 10, 11]:
        season = "autumn"
    else:
        raise Exception("Something went totally wrong!")
    return season