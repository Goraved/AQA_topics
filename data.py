import asyncio
import os
from datetime import date

from mysql import connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

DB: MySQLConnection = None


def db_connection():
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
    global DB
    if DB:
        DB.close()


def query(sql: str) -> MySQLCursor:
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
    return str(text).lstrip().rstrip().replace("<", "").replace(">", "")


async def get_season() -> str:
    await asyncio.sleep(0)
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
