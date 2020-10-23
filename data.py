import asyncio
import os
from datetime import date

import MySQLdb
from MySQLdb.cursors import Cursor

DB = None


def db_connection():
    global DB
    DB = MySQLdb.connect(user=os.environ['DB_USER'], password=os.environ['DB_PASS'],
                         host=os.environ['DB_HOST'], charset='utf8',
                         database=os.environ['DB'], connect_timeout=600)
    try:
        cursor = DB.cursor()
        cursor.execute("""SET NAMES 'utf8';
    SET CHARACTER SET 'utf8';
    SET SESSION collation_connection = 'utf8_general_ci';""")
    except:
        pass


def close_connection():
    global DB
    if DB:
        DB.close()


def query(sql: str) -> Cursor:
    if not DB:
        db_connection()

    try:
        cursor = DB.cursor()
        cursor.execute(sql)
        DB.commit()
    except:
        db_connection()
        # DB.ping(True)
        cursor = DB.cursor()
        cursor.execute(sql)
        DB.commit()
    return cursor


def reformat_text(text: str) -> str:
    return str(text).lstrip().rstrip().replace('<', '').replace('>', '')


async def get_season() -> str:
    await asyncio.sleep(0)
    current_month = date.today().month
    if current_month in [12, 1, 2]:
        season = 'winter'
    elif current_month in [3, 4, 5]:
        season = 'spring'
    elif current_month in [6, 7, 8]:
        season = 'summer'
    elif current_month in [9, 10, 11]:
        season = 'autumn'
    else:
        raise Exception('Something went totally wrong!')
    return season
