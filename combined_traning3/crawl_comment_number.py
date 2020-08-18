from bs4 import BeautifulSoup
import requests
import selenium
from selenium import webdriver  # selenium 프레임 워크에서 webdriver 가져오기
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')



url = 'https://n.news.naver.com/mnews/article/comment/032/0003027337?sid=100'

from webdriver_manager.chrome import ChromeDriverManager

browser.get(url)
#a = soup.select('u_cbox_contents')
html = browser.page_source
soup = BeautifulSoup(html, 'lxml')
print(soup)