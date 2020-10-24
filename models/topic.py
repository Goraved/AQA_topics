import asyncio
from datetime import date, timedelta
from typing import List

import requests

from data import query, reformat_text
from models.domain import check_link_in_whitelist


class Topic:
    def __init__(self, name: str, link: str, category_id: int, topic_id: int = None, category_name: str = None,
                 date_added=None, is_new: bool = None):
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
        query(f"Delete from topics where id = {topic_id}")

    def update_topic(self):
        query(f"Update topics set title='{reformat_text(self.name)}', link='{reformat_text(self.link)}', "
              f"category_id={self.category_id} where id = {self.topic_id}")

    @staticmethod
    def check_if_topic_is_new(topic_date: date) -> bool:
        return date.today() - topic_date < timedelta(days=7)

    def create_topic(self):
        # Async gathering of data
        ioloop = asyncio.new_event_loop()
        asyncio.set_event_loop(ioloop)
        async_values = ioloop.run_until_complete(asyncio.gather(*[get_topics()]))
        topics = async_values[0]
        for topic in topics:
            if self.name.lower() == topic.name.lower() or self.link.lower() == topic.link.lower():
                return f'Topic already added with title "{topic.name}"'
        try:
            if 'dou' in self.link:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67',
                    'Referer': 'https://dou.ua',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                response = requests.get(self.link, headers=headers)
            else:
                response = requests.get(self.link)
        except Exception as exception:
            return f'Bad url - {exception.args[0]}'
        if str(response.status_code)[0] == '2' or check_link_in_whitelist(self.link):
            query('Insert into topics (category_id, title, link, added_date) values ({},"{}","{}","{}")'
                  .format(self.category_id, reformat_text(self.name), reformat_text(self.link), date.today()))
        else:
            message = f'Link "{self.link}" is broken | Code = {response.status_code}'
            query(f"Insert into error_log (text, date) values ('{message}', '{date.today()}')")
            return message


async def get_topics() -> List[Topic]:
    await asyncio.sleep(0)
    topics = []
    cur = query("""Select t.id, t.category_id, t.title, t.link, t.added_date, c.title  from topics as t
                JOIN categories as c on t.category_id = c.id
                 order by category_id, id DESC""")
    for row in cur.fetchall():
        topics.append(Topic(topic_id=row[0], category_id=row[1], name=row[2], link=row[3], date_added=row[4],
                            category_name=row[5], is_new=Topic.check_if_topic_is_new(row[4])))
    return topics


def search_topics(search_request: str) -> List[Topic]:
    topics = []
    cur = query(f"""select t.title, t.link, c.title, c.id from topics as t
join categories as c on t.category_id = c.id
where t.title like '% {search_request}%' or t.title like '{search_request}%' or t.title like '[{search_request}%'
order by c.id, t.title""")
    for row in cur.fetchall():
        topics.append(Topic(name=row[0], link=row[1], category_id=row[3], category_name=row[2]))
    return topics


def index_topics_by_category(topics: List[Topic]):
    previous_cat = 0
    index = 0
    for topic in topics:
        if topic.category_id == previous_cat:
            index += 1
            topic.index = index
        else:
            index = 0
            topic.index = index
        previous_cat = topic.category_id
