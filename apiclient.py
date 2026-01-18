import dataclasses
from datetime import date, datetime
import os

from bs4 import BeautifulSoup
import requests


def must[T](v: T | None) -> T:
    assert v is not None
    return v


@dataclasses.dataclass
class CheckedOutItem:
    title: str
    author: str
    barcode: str
    due_date: date


SESSIONS_URI = (
    'https://gateway.bibliocommons.com/v2/libraries/kcls/sessions'
)


class KCLSClient:
    def __init__(self, username: str, password: str):
        r = requests.post(
            SESSIONS_URI,
            json={
                'username': username,
                'password': password,
            },
        )
        r.raise_for_status()

        self.session_id = r.json()['auth']['sessionId']
        self.auth_token = r.json()['auth']['authToken']

    def get_checked_out_items(self) -> list[CheckedOutItem]:
        r = requests.get(
            'https://kcls.bibliocommons.com/v2/print/checkedout/out',
            cookies={
                'session_id': self.session_id,
                'bc_access_token': self.auth_token,
            },
        )
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'html.parser')
        table = must(soup.select_one('div.cp-print-table table'))

        items = []
        for row in table.select('tbody tr'):

            def t(css: str):
                return must(row.select_one(css)).text

            title = t('td.item-title')
            author = t('td.item-author')
            barcode = t('td.item-callnumber p.barcode')
            due = t(
                'td.item-status div.cp-checked-out-status-overview > div:nth-child(1) > span.field-value'
            )
            due_date = datetime.strptime(due, '%b %d, %Y').date()

            items.append(CheckedOutItem(title, author, barcode, due_date))

        return items

def default_client() -> KCLSClient:
    return KCLSClient(os.environ['KCLS_USERNAME'], os.environ['KCLS_PASSWORD'])
