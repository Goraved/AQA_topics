from data import query


class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def get_user(username: str) -> User:
    users = []
    cur = query(f"select username, password from aqa where username like '{username}'")
    for row in cur.fetchall():
        users.append(User(username=row[0], password=row[1]))
    return users[0]
