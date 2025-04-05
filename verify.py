from functools import wraps

from flask import request, Response

from models.user import get_user


def check_auth(username: str, password: str) -> bool:
    """
    This function is called to check if a username /
    password combination is valid.

    Args:
        username (str): The username to authenticate.
        password (str): The password to authenticate.

    Returns:
        bool: True if the username and password combination is valid, False otherwise.
    """
    user = get_user(username)
    return str(username) == user.username and str(password) == user.password

def authenticate():
    """
    Sends a 401 response that enables basic auth.

    Returns:
        Response: A Flask response object with a 401 status code and a WWW-Authenticate header.
    """
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(func):
    """
    A decorator that ensures the decorated function requires HTTP Basic Authentication.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function that requires authentication.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(str(auth.username), str(auth.password)):
            return authenticate()
        return func(*args, **kwargs)

    return decorated