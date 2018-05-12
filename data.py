import time

import MySQLdb


def query(sql):
    db = MySQLdb.connect(user='aqatopics', password='Hw1gK!!v4hiP',
                         host='den1.mysql5.gear.host',
                         database='aqatopics', connect_timeout=600)
    try:
        cursor = db.cursor()
        cursor.execute("""SET NAMES 'utf8';
    SET CHARACTER SET 'utf8';
    SET SESSION collation_connection = 'utf8_general_ci';""")
    except:
        pass
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except (AttributeError, MySQLdb.OperationalError):
        db.ping(True)
        cursor = db.cursor()
        cursor.execute(sql)
    db.commit()
    db.close()
    return cursor


def get_header_topics():
    topics = []
    cur = query("Select * from topics where category_id = 4")
    for row in cur.fetchall():
        topics.append({'category_id': row[1], 'title': row[2], 'link': row[3], 'comments': row[4]})
    cur.close()
    return topics


def get_topics():
    topics = []
    cur = query("Select * from topics")
    for row in cur.fetchall():
        topics.append({'category_id': row[1], 'title': row[2], 'link': row[3], 'comments': row[4]})
    cur.close()
    return topics


def create_topic(title, link, category):
    query('Insert into topics (category_id, title, link) values ({},"{}","{}")'.format(category, title, link))


def get_categories():
    categories = []
    cur = query("Select * from categories where id <> 4")
    for row in cur.fetchall():
        categories.append({'id': row[0], 'title': row[1], 'comments': row[2], 'icon': row[3]})
    cur.close()
    return categories


def get_categories_list():
    categories = []
    cur = query("Select id, title from categories")
    for row in cur.fetchall():
        categories.append({'id': row[0], 'title': row[1]})
    cur.close()
    return categories


def save_statistics(results):
    # Get skill list
    skills = {}
    cur = query("Select * from skills")
    for row in cur.fetchall():
        skills.update({row[1]: row[0]})
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from statistics where date_collected = '%s'" % date)
    for result in results:
        # Get skill id
        skill_id = skills.get(result)
        # Save statistic by skill
        insert_query = "Insert into statistics (skill_id, skill_percent, date_collected) values (%s,'%s','%s');" % (
            skill_id, results.get(result), date)
        cur = query(insert_query)
    cur.close()
#
#
#
# def close_db():
#     db.close()
