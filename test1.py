import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')

UN = os.environ['KCLS_USERNAME']
PW = os.environ['KCLS_PASSWORD']

with webdriver.Chrome(options) as driver:
  driver.get('https://kcls.bibliocommons.com/user/login?destination=https://kcls.bibliocommons.com/v2/checkedout')

  username_el = driver.find_element(By.CSS_SELECTOR, 'input[type=text][data-js=username_login]')
  username_el.send_keys(UN)

  password_el = driver.find_element(By.CSS_SELECTOR, 'input[type=password][data-js=user_pin]')
  password_el.send_keys(PW)

  login_el = driver.find_element(By.CSS_SELECTOR, 'input[type=submit][data-js=button_login]')
  login_el.click()

  # Here we're relying on the fact our original URL included a redirect to the
  # "Checked Out" page of the user dashboard.

  title_el = WebDriverWait(driver, 10.0).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.cp-borrowing-utility-bar-title'))
  )

  for item_el in driver.find_elements(By.CSS_SELECTOR, 'div[data-key=check-out-list-item]'):
    def t(css):
      try:
        return item_el.find_element(By.CSS_SELECTOR, css).text
      except NoSuchElementException:
        return ''
  
    print('Title:', t('a[data-key=bib-title] span.title-content'))
    print('Author:', t('a[data-key=author-link]'))
    print('Due:', t('div.cp-checked-out-due-on').removeprefix('Due by '))
    print()
