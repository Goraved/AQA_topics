import asyncio
from typing import List

from data import query, reformat_text
from models.topic import Topic


class Category:
    def __init__(self, name: str, icon: str, category_id: int = None):
        self.name = name
        self.icon = icon
        self.category_id = category_id
        self.count = 0
        self.index = 0

    def create_category(self):
        query(f"Insert into categories (title, icon) values ('{reformat_text(self.name)}', '{self.icon}')")

    def update_category(self):
        query(f"Update categories set title='{reformat_text(self.name)}', icon='{self.icon}'"
              f" WHERE id = {self.category_id}")

    @staticmethod
    def remove_category(category_id: int):
        query(f"Delete from categories WHERE id = {category_id}")


async def get_categories() -> List[Category]:
    await asyncio.sleep(0)
    categories = []
    cur = query("SELECT * from categories")
    for row in cur.fetchall():
        categories.append(Category(name=row[1], category_id=row[0], icon=row[3]))
    cur.close()
    return categories


def count_of_topic_in_cat(categories: List[Category], topics: List[Topic]):
    index, item = 0, 0
    for category in categories:
        count = 0
        for topic in topics:
            if topic.category_id == category.category_id:
                count += 1
        category.count = count
        if category.category_id != 4 and category.count != 0:
            category.index = index
            index += 1
        item += 1
