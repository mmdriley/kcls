import dataclasses
from datetime import date, datetime
import os
import asyncio

from bs4 import BeautifulSoup
import httpx


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
        self.session_id = None
        self.auth_token = None
        self.client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client:
            return self.client
        return httpx.AsyncClient()

    async def async_login(self, username: str, password: str):
        # If we own the client (it was created ad-hoc), we should close it?
        # Actually, for the ad-hoc case in the sync wrapper, we probably want a context manager.
        # Let's simplify: always use a context manager for the ad-hoc case.
        
        if self.client:
             await self._perform_login(self.client, username, password)
        else:
            async with httpx.AsyncClient() as client:
                await self._perform_login(client, username, password)

    async def _perform_login(self, client: httpx.AsyncClient, username: str, password: str):
        r = await client.post(
            SESSIONS_URI,
            json={
                'username': username,
                'password': password,
            },
        )
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError('Invalid credentials') from e
            raise

        self.session_id = r.json()['auth']['sessionId']
        self.auth_token = r.json()['auth']['authToken']

    def login(self, username: str, password: str):
        asyncio.run(self.async_login(username, password))

    async def async_get_checked_out_items(self) -> list[CheckedOutItem]:
        if self.client:
            return await self._perform_get_checked_out_items(self.client)
        else:
            async with httpx.AsyncClient() as client:
                return await self._perform_get_checked_out_items(client)

    async def _perform_get_checked_out_items(self, client: httpx.AsyncClient) -> list[CheckedOutItem]:
        r = await client.get(
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

    def get_checked_out_items(self) -> list[CheckedOutItem]:
        return asyncio.run(self.async_get_checked_out_items())


def default_client() -> KCLSClient:
    client = KCLSClient()
    client.login(os.environ['KCLS_USERNAME'], os.environ['KCLS_PASSWORD'])
    return client
