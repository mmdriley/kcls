from datetime import datetime
import os

from bs4 import BeautifulSoup
import requests


def must[T](v: T | None) -> T:
    assert v is not None
    return v


def main():
    sessions_uri = ('https://gateway.bibliocommons.com/v2/libraries/(libraryName)/sessions'.replace('(libraryName)', 'kcls'))

    r = requests.post(sessions_uri, json={
        'username': os.environ['KCLS_USERNAME'],
        'password': os.environ['KCLS_PASSWORD'],
    })
    r.raise_for_status()

    session_id = r.json()['auth']['sessionId']
    auth_token = r.json()['auth']['authToken']
    # user_id = r.json()['auth']['currentUserId']

    r = requests.get('https://kcls.bibliocommons.com/v2/print/checkedout/out', cookies={
        'session_id': session_id,
        'bc_access_token': auth_token,
    })
    r.raise_for_status()

    # we could also be pulling this information from the JSON in
    # `body > script:nth-child(2)`

    soup = BeautifulSoup(r.text, 'html.parser')
    table = must(soup.select_one('div.cp-print-table table'))
    for row in table.select('tbody tr'):
        title = must(row.select_one('td.item-title')).text
        author = must(row.select_one('td.item-author')).text
        barcode = must(row.select_one('td.item-callnumber p.barcode')).text
        due = must(row.select_one('td.item-status div.cp-checked-out-status-overview > div:nth-child(1) > span.field-value')).text
        due_date = datetime.strptime(due, '%b %d, %Y').date()  # e.g. Dec 29, 2025

        print(f'{title} // {author} // {barcode} // {due_date}')


if __name__ == '__main__':
    main()
