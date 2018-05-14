import MySQLdb


def query(sql):
    db = MySQLdb.connect(user='aqatopics', password='Hw1gK!!v4hiP',
                         host='den1.mysql5.gear.host', charset='utf8',
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


# Topics
def create_topic(title, link, category):
    query('Insert into topics (category_id, title, link) values ({},"{}","{}")'.format(category, title, link))


def update_topic(id, title, link, category):
    query("Update topics set title='{}', link='{}', category_id={} where id = {}".format(title, link, category, id))


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


def create_category(title):
    query("Insert into categories (title) values ('{}')".format(title))


def update_category(id, title, icon):
    query("Update categories set title='{}', icon='{}' where id = {}".format(title, icon, id))


def remove_category(id):
    query("Delete from categories where id = {}".format(id))
