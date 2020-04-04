import asyncio
import os
from datetime import date, timedelta

import MySQLdb
import requests

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


def query(sql):
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
            return f'Topic already added with title "{topic["title"]}"'
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
    except Exception as e:
        return f'Bad url - {e.args[0]}'
    # TODO add whitelist to DB
    if str(response.status_code)[0] == '2' or check_link_in_whitelist(link):
        query('Insert into topics (category_id, title, link, added_date) values ({},"{}","{}","{}")'
              .format(category, reformat_text(title), reformat_text(link), date.today()))
    else:
        message = f'Link "{link}" is broken | Code = {response.status_code}'
        query(f"Insert into error_log (text, date) values ('{message}', '{date.today()}')")
        return message


def check_link_in_whitelist(link):
    for domain in get_domains_list():
        if domain in link:
            return True
    return False


def update_topic(id, title, link, category):
    query(
        f"Update topics set title='{reformat_text(title)}', link='{reformat_text(link)}', category_id={category} where id = {id}")


def search_topics(search_request):
    topics = []
    cur = query(f"""select t.title, t.link, c.title from topics as t
join categories as c on t.category_id = c.id
where t.title like '% {search_request}%' or t.title like '{search_request}%' or t.title like '[{search_request}%'
order by c.id, t.title""")
    for row in cur.fetchall():
        topics.append({'topic': row[0], 'link': row[1], 'category': row[2]})
    return topics


def get_user(username):
    users = []
    cur = query(f"select username, password from aqa where username like '{username}'")
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
    query(f"Delete from topics where id = {id}")


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
    query(f"Insert into categories (title, icon) values ('{reformat_text(title)}', '{icon}')")


def update_category(id, title, icon):
    query(f"Update categories set title='{reformat_text(title)}', icon='{icon}' where id = {id}")


def remove_category(id):
    query(f"Delete from categories where id = {id}")


async def get_domains():
    await asyncio.sleep(0)
    cur = query("Select domain from whitelist")
    domains = [_[0] for _ in cur.fetchall()]
    return domains


def get_domains_list():
    cur = query("Select domain from whitelist")
    domains = [_[0] for _ in cur.fetchall()]
    return domains


def create_domain(domain):
    query(f"Insert into whitelist  values ('{domain}')")


def update_domain(old_domain, new_domain):
    query(f"Update whitelist set domain='{new_domain}' where domain = '{old_domain}'")


def remove_domain(domain):
    query(f"Delete from whitelist where domain = '{domain}'")


def check_if_topic_is_new(topic_date):
    return date.today() - topic_date < timedelta(days=7)


async def get_season():
    await asyncio.sleep(0)
    current_month = date.today().month
    if current_month in [12, 1, 2]:
        return 'winter'
    elif current_month in [3, 4, 5]:
        return 'spring'
    elif current_month in [6, 7, 8]:
        return 'summer'
    elif current_month in [9, 10, 11]:
        return 'autumn'
    else:
        raise Exception('Something went totally wrong!')
