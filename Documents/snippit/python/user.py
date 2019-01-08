import python.utils as utils
from python.snippit_sql import *
import json


def add_new_user(username, password):
    pass


def edit_user(user_id, username, password):
    pass


def check_login(user_name, passwd):
    """check username and passwd and return user_id if they match the users table info
    """
    query = """SELECT user_id from users WHERE username = '{}' 
            AND password = '{}';""".format(
        user_name, passwd
    )
    res = run_query(query)
    if res:
        return res[0]
    return None


# test
print(check_login("gilad", "123456"))
