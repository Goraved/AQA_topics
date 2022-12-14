from data import query


class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def get_user(username: str) -> User:
    users = []
    cur = query(f"SELECT username, password from aqa WHERE username like '{username}'")
    for row in cur.fetchall():
        users.append(User(username=row[0], password=row[1]))
    cur.close()
    return users[0]
