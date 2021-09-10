import getpass
import sys

import vk_api
from vk_api import exceptions

# We receive data from the user
login = input("Enter your login: ")


def captcha_handler(captcha):
    key = input(f"Enter the code from the image {captcha.get_url().strip()}: ")

    # We are trying to send a request with a captcha again
    return captcha.try_again(key)


def two_factor_auth_handler():
    key = input("Enter the authorization code: ")
    remember_device = True

    return key, remember_device


# Authorization
try:
    vk_session = vk_api.VkApi(login, captcha_handler=captcha_handler)
    vk_session.auth()
    print("Authorized using cookies")
except exceptions.PasswordRequired as e:
    if sys.stdin.isatty():
        password = getpass.getpass("Enter your password: ")
    else:
        password = input("Enter your password: ")
    vk_session = vk_api.VkApi(login, password, auth_handler=two_factor_auth_handler, captcha_handler=captcha_handler)
    vk_session.auth()
    print("Authorized with a password")

vk = vk_session.get_api()

me = vk.users.get()[0]

print(f"Auth as {me.get('first_name')} {me.get('last_name')}")

tools = vk_api.VkTools(vk)
groups = tools.get_all_iter("groups.get", 1000, {"extended": "1", "fields": "members_count"})
for group in groups:
    if group.get("members_count", 99999999) <= 10:
        print(f'Leave "{group.get("name", "")}" (id={group.get("id", "")})', end=" ")
        if vk.groups.leave(group_id=group.get("id", "")):
            print("ok")
        else:
            print("failed")
