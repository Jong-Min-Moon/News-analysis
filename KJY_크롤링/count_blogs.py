import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
def get_news_num(oneday, query):
    url = """https://search.naver.com/search.naver?date_from={}&date_option=8&date_to={}&dup_remove=1&nso=a%3At%2Cp%3Afrom20200613to20200613&post_blogurl=&post_blogurl_without=&query=%{}&sm=tab_pge&srchby=title&st=sim&where=post&start=1""".format(oneday, oneday, query)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    total_news = soup.find('span', 'title_num') # 검색 결과 개수 가져오기
    if isinstance(total_news , type(None)):
        print(oneday, ', 0')
    else:
        total_news = re.split(' / ', total_news.text)[1][0:-1] # 1-10 / 629건 과 같은 형식에서 629만 가져오기. '/'로 쪼갠 다음, '건'을 지운다.
        total_news = int(total_news.replace(',','')) #
        print(oneday, ', ', total_news)

crawl_range = pd.date_range('2020.07.10', '2020.07.14')

for crawl_date_obj in crawl_range:
    get_news_num(crawl_date_obj.strftime('%Y%m%d'), '백선엽')