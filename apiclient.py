import dataclasses
from datetime import date, datetime

import httpx
from bs4 import BeautifulSoup


def must[T](v: T | None) -> T:
    assert v is not None
    return v


@dataclasses.dataclass
class CheckedOutItem:
    title: str
    author: str
    barcode: str
    due_date: date


SESSIONS_URI = 'https://gateway.bibliocommons.com/v2/libraries/kcls/sessions'


class KCLSClient:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.session_id: str | None = None
        self.auth_token: str | None = None
        self.client = client or httpx.AsyncClient()

    async def login(self, username: str, password: str):
        r = await self.client.post(
            SESSIONS_URI,
            json={
                'username': username,
                'password': password,
            },
        )
        if r.status_code == 401:
            raise ValueError('Invalid credentials')  # prettier error for common case
        r.raise_for_status()

        self.session_id = r.json()['auth']['sessionId']
        self.auth_token = r.json()['auth']['authToken']

    async def get_checked_out_items(self) -> list[CheckedOutItem]:
        assert self.session_id and self.auth_token

        r = await self.client.get(
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

            title = t('td.item-title .main-title')
            sub_title = t('td.item-title .sub-title')

            if sub_title:
                title = f'{title}: {sub_title}'

            author = t('td.item-author')
            barcode = t('td.item-callnumber p.barcode')
            due = t(
                'td.item-status div.cp-checked-out-status-overview > div:nth-child(1) > span.field-value'
            )
            due_date = datetime.strptime(due, '%b %d, %Y').date()

            items.append(CheckedOutItem(title, author, barcode, due_date))

        return items
