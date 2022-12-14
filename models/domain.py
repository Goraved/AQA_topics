import asyncio
from typing import List

from data import query


async def get_domains() -> List[str]:
    await asyncio.sleep(0)
    cur = query("SELECT domain from whitelist")
    domains = [_[0] for _ in cur.fetchall()]
    cur.close()
    return domains


def check_link_in_whitelist(link: str) -> bool:
    for domain in Domain.get_domains_list():
        if domain in link:
            return True
    return False


class Domain:
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def get_domains_list() -> List[str]:
        cur = query("SELECT domain from whitelist")
        domains = [_[0] for _ in cur.fetchall()]
        cur.close()
        return domains

    def create_domain(self):
        query(f"Insert into whitelist  values ('{self.name}')")

    def update_domain(self, new_domain: str):
        query(f"Update whitelist set domain='{new_domain}' WHERE domain = '{self.name}'")

    def remove_domain(self):
        query(f"Delete from whitelist WHERE domain = '{self.name}'")
