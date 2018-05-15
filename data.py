import os

import MySQLdb


def query(sql):
    db = MySQLdb.connect(user=os.environ['DB_USER'], password=os.environ['DB_PASS'],
                         host=os.environ['DB_HOST'], charset='utf8',
                         database=os.environ['DB'], connect_timeout=600)
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


# Topics
def create_topic(title, link, category):
    query('Insert into topics (category_id, title, link) values ({},"{}","{}")'.format(category, reformat_text(title),
                                                                                       reformat_text(link)))


def update_topic(id, title, link, category, **kwargs):
    query(
        "Update topics set title='{}', link='{}', category_id={} where id = {}".format(reformat_text(title),
                                                                                       reformat_text(link), category,
                                                                                       id))


def get_user(username):
    users = []
    cur = query("select username, password from aqa where username like '{}'".format(username))
    for row in cur.fetchall():
        users.append({'username': row[0], 'pass': row[1]})
    cur.close()
    return users[0]


def get_topics():
    topics = []
    cur = query("Select * from topics")
    for row in cur.fetchall():
        topics.append({'id': row[0], 'category_id': row[1], 'title': row[2], 'link': row[3], 'comments': row[4]})
    cur.close()
    return topics


def remove_topic(id):
    query("Delete from topics where id = {}".format(id))


# Categories
def get_categories():
    categories = []
    cur = query("Select * from categories")
    for row in cur.fetchall():
        categories.append({'id': row[0], 'title': row[1], 'comments': row[2], 'icon': row[3]})
    cur.close()
    return categories


def count_of_topic_in_cat(categories, topics):
    index, item = 0, 0
    for category in categories:
        count = 0
        for topic in topics:
            if topic['category_id'] == category['id']:
                count += 1
        category['count'] = count
        if category['id'] != 4 and category['count'] != 0:
            category['index'] = index
            index += 1
        item += 1


def reformat_text(text):
    return str(text).lstrip().rstrip().replace('<', '').replace('>', '')


def create_category(title):
    query("Insert into categories (title) values ('{}')".format(reformat_text(title)))


def update_category(id, title, icon):
    query("Update categories set title='{}', icon='{}' where id = {}".format(reformat_text(title), icon, id))


def remove_category(id):
    query("Delete from categories where id = {}".format(id))
