from collections.abc import Iterable
import dataclasses
from datetime import datetime
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')


def login_as(driver: RemoteWebDriver, username: str, password: str):
  driver.get('https://kcls.bibliocommons.com/user/login')

  username_el = driver.find_element(By.CSS_SELECTOR, 'input[type=text][data-js=username_login]')
  username_el.send_keys(username)

  password_el = driver.find_element(By.CSS_SELECTOR, 'input[type=password][data-js=user_pin]')
  password_el.send_keys(password)

  login_el = driver.find_element(By.CSS_SELECTOR, 'input[type=submit][data-js=button_login]')
  login_el.click()

  # Wait for the form submit to result in a navigation away
  WebDriverWait(driver, 10.0).until(
      EC.staleness_of(login_el)
  )


@dataclasses.dataclass
class CheckedOutItem:
  title: str
  author: str  # may be ""
  barcode: str

  due_date: datetime


def checked_out_items(driver: RemoteWebDriver) -> Iterable[CheckedOutItem]:
  driver.get('https://kcls.bibliocommons.com/v2/checkedout')

  # Wait for AJAX to settle
  WebDriverWait(driver, 10.0).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.cp-borrowing-utility-bar-title'))
  )

  for item_el in driver.find_elements(By.CSS_SELECTOR, 'div[data-key=check-out-list-item]'):
    def t(css):
      try:
        return item_el.find_element(By.CSS_SELECTOR, css).text
      except NoSuchElementException:
        return ''
  
    title = t('a[data-key=bib-title] span.title-content')
    author = t('a[data-key=author-link]')  # sometimes missing

    due_date_str = t('div.cp-checked-out-due-on').removeprefix('Due by ')
    due_date = datetime.strptime(due_date_str, '%b %d, %Y')  # e.g. Dec 29, 2025

    barcode = t('div.cp-barcode-field span.field-value')

    yield CheckedOutItem(title, author, barcode, due_date)


creds = os.environ['KCLS_CREDS']

for cred in creds.splitlines():
  if not cred:  # e.g. blank line
    continue

  un, pw = cred.split(':', 2)

  with webdriver.Chrome(options) as driver:
    login_as(driver, un, pw)

    for it in checked_out_items(driver):
      print(f'{it.due_date:%Y-%m-%d} {it.barcode:<20}')
      print(f'  {it.title:>40} {it.author:>20}')
