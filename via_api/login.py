import os

import requests

sessions_uri = ('https://gateway.bibliocommons.com/v2/libraries/(libraryName)/sessions'.replace('(libraryName)', 'kcls'))

r = requests.post(sessions_uri, json={
    'username': os.environ['KCLS_USERNAME'],
    'password': os.environ['KCLS_PASSWORD'],
})
r.raise_for_status()

session_id = r.json()['auth']['sessionId']
auth_token = r.json()['auth']['authToken']
user_id = r.json()['auth']['currentUserId']
# print(session_id)


holds_uri = 'https://kcls.bibliocommons.com/user_stats/borrowing?section=checkedout'
r = requests.get(holds_uri, cookies={
    'session_id': session_id,
})
r.raise_for_status()
print(r.json())


# checkedout_api = 'https://gateway.bibliocommons.com/v2/libraries/kcls/borrowing/summaries?accountId=' + str(user_id)
# r = requests.get(checkedout_api, headers={
#     'X-Session-Id': session_id,
#     'X-Auth-Token': auth_token,
# })
# r.raise_for_status()

# print(r.text)
