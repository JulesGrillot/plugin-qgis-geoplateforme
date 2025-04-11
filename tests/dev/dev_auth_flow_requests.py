#! python3  # noqa: E265

"""
Quick and dirty test of API authentication and basic usage.

Additionnal dependencies:

- requests

Usage:

1. change the username in the script
2. store your password in an environment variable named `GPF_USER_PASSWORD`.
Typically:

- Bash: `export GPF_USER_PASSWORD='my_password'`
- PowerShell: `$env:GPF_USER_PASSWORD = 'my_password'`
3. run:

- Linux: `python3 dev_auth_flow_requests.py`
- Windows: `py -3 dev_auth_flow_requests.py`

BE CAREFUL: do not commit if you write your credentials in the code
"""

# standard
import pprint
from os import getenv
from sys import exit

# 3rd party
import requests

USER_NAME = ""
USER_PASSWORD = getenv("GPF_USER_PASSWORD")
CLIENT_ID = "guichet"
TOKEN_URL = "https://iam-ign-qa-ext.cegedim.cloud/auth/realms/demo/protocol/openid-connect/token"
API_URL = "https://plage-geoplateforme.cegedim.cloud/api/v1/"


# -- FUNCTIONS
def get_with_token(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers)


# -- MAIN SCRIPT
post_data = {
    "grant_type": "password",
    "client_id": CLIENT_ID,
    "username": USER_NAME,
    "password": USER_PASSWORD,
}


token = requests.post(TOKEN_URL, data=post_data)
token_as_json = token.json()
if "error" in token_as_json:
    err_msg = f"Error obtaining an auth token: {token_as_json.get('error')}"
    exit(err_msg)

print("\n\n\tTOKEN")
pprint.pprint(token_as_json)


url_user = f"{API_URL}users/me"
user_info = get_with_token(url_user, token_as_json.get("access_token"))
user_info_as_json = user_info.json()
if "error" in user_info_as_json:
    err_msg = f"Error obtaining an auth token: {user_info_as_json.get('error')}"
    exit(err_msg)

print("\n\n\tUSER INFO")
pprint.pprint(user_info_as_json)
