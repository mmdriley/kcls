from datetime import datetime
import os

from bs4 import BeautifulSoup
import requests


def must[T](v: T | None) -> T:
    assert v is not None
    return v


def main(username: str, password: str):
    sessions_uri = (
        'https://gateway.bibliocommons.com/v2/libraries/(libraryName)/sessions'.replace(
            '(libraryName)', 'kcls'
        )
    )

    r = requests.post(
        sessions_uri,
        json={
            'username': username,
            'password': password,
        },
    )
    r.raise_for_status()

    session_id = r.json()['auth']['sessionId']
    auth_token = r.json()['auth']['authToken']
    # user_id = r.json()['auth']['currentUserId']

    r = requests.get(
        'https://kcls.bibliocommons.com/v2/print/checkedout/out',
        cookies={
            'session_id': session_id,
            'bc_access_token': auth_token,
        },
    )
    r.raise_for_status()

    # we could also be pulling this information from the JSON in
    # `body > script:nth-child(2)`

    soup = BeautifulSoup(r.text, 'html.parser')
    table = must(soup.select_one('div.cp-print-table table'))
    for row in table.select('tbody tr'):

        def t(css: str):
            return must(row.select_one(css)).text

        title = t('td.item-title')
        author = t('td.item-author')
        barcode = t('td.item-callnumber p.barcode')
        due = t(
            'td.item-status div.cp-checked-out-status-overview > div:nth-child(1) > span.field-value'
        )
        due_date = datetime.strptime(due, '%b %d, %Y').date()  # e.g. Dec 29, 2025

        print(f'{title} // {author} // {barcode} // {due_date}')


if __name__ == '__main__':
    main(os.environ['KCLS_USERNAME'], os.environ['KCLS_PASSWORD'])
