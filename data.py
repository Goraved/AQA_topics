import asyncio
import os
from datetime import date, timedelta

import MySQLdb
import requests


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
    # Async gathering of data
    ioloop = asyncio.new_event_loop()
    asyncio.set_event_loop(ioloop)
    async_values = ioloop.run_until_complete(asyncio.gather(*[get_topics()]))
    topics = async_values[0]
    for topic in topics:
        if title != topic['title'] and link != topic['link']:
            continue
        else:
            return 'Topic already added with title "{}"'.format(topic['title'])
    try:
        if 'dou' in link:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67',
                'Referer': 'https://dou.ua',
                'X-Requested-With': 'XMLHttpRequest'
            }
            response = requests.get(link, headers=headers)
        else:
            response = requests.get(link)
    except:
        return 'Bad url'
    if response.status_code == 200:
        query(
            'Insert into topics (category_id, title, link, added_date) values ({},"{}","{}","{}")'
                .format(category, reformat_text(title), reformat_text(link), date.today()))
    else:
        message = 'Link "{}" is broken | Code = {}'.format(link, response.status_code)
        query("Insert into error_log (text, date) values ('{}', '{}')".format(message,
                                                                              date.today()))
        return message


def update_topic(id, title, link, category):
    query(
        "Update topics set title='{}', link='{}', category_id={} where id = {}".format(reformat_text(title),
                                                                                       reformat_text(link), category,
                                                                                       id))


def search_topics(search_request):
    topics = []
    cur = query("""select t.title, t.link, c.title from topics as t
join categories as c on t.category_id = c.id
where t.title like '% {}%' or t.title like '{}%'
order by c.id, t.title""".format(search_request, search_request))
    for row in cur.fetchall():
        topics.append({'topic': row[0], 'link': row[1], 'category': row[2]})
    return topics


def get_user(username):
    users = []
    cur = query("select username, password from aqa where username like '{}'".format(username))
    for row in cur.fetchall():
        users.append({'username': row[0], 'pass': row[1]})
    return users[0]


async def get_topics():
    await asyncio.sleep(0)
    topics = []
    cur = query("""Select t.id, t.category_id, t.title, t.link, t.comments, t.added_date, c.title  from topics as t
JOIN categories as c on t.category_id = c.id
 order by category_id, id DESC""")
    for row in cur.fetchall():
        topics.append(
            {'id': row[0], 'category_id': row[1], 'title': row[2], 'link': row[3], 'comments': row[4], 'date': row[5],
             'new': check_if_topic_is_new(row[5]), 'category': row[6]})
    return topics


def remove_topic(id):
    query("Delete from topics where id = {}".format(id))


# Categories
async def get_categories():
    await asyncio.sleep(0)
    categories = []
    cur = query("Select * from categories")
    for row in cur.fetchall():
        categories.append({'id': row[0], 'title': row[1], 'comments': row[2], 'icon': row[3]})
    return categories


def index_topics_by_category(topics):
    previous_cat = 0
    index = 0
    for topic in topics:
        if topic['category_id'] == previous_cat:
            index += 1
            topic['index'] = index
        else:
            index = 0
            topic['index'] = index
        previous_cat = topic['category_id']


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


def create_category(title, icon):
    query("Insert into categories (title, icon) values ('{}', '{}')".format(reformat_text(title), icon))


def update_category(id, title, icon):
    query("Update categories set title='{}', icon='{}' where id = {}".format(reformat_text(title), icon, id))


def remove_category(id):
    query("Delete from categories where id = {}".format(id))


def check_if_topic_is_new(topic_date):
    return date.today() - topic_date < timedelta(days=7)
