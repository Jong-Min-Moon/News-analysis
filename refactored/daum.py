from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

def get_url_daum_news(query, s_date, e_date):
#ex. get_url_daum(query = '코로나', s_date = '20200217230014', e_date = '20200317230014')

#1. 탐색할 페이지 수 결정하기
  url_search_result = 'https://search.daum.net/search?w=news&sort=recency&q='+query+'&cluster=n&DA=PGD&dc=STC&pg=1&r=1&p=1&rc=1&at=more&sd='+s_date+'&ed='+ e_date + '&period=u'
  print(url_search_result)
    #1.3.2. 다음 기사 개수
  response = requests.get(url_search_result)
  html = response.text
  soup = BeautifulSoup(html, 'html.parser')
  print(soup)

  total_news = soup.find('span', 'txt_info') # 검색 결과 개수 가져오기
  
  total_news = re.split(' / ', total_news.text)[1][0:-1] # 1-10 / 629건 과 같은 형식에서 629만 가져오기
  total_news = total_news.replace('약 ','')
  total_news = int(total_news.replace(',',''))

  print('total news:', total_news)
  total_pages = math.ceil(total_news/10)   
  print('pages:', total_pages)

  
#1.4.2. 다음 링크 추출
  links = []
  for i in range(1, total_pages+1):
    url_search_result = 'https://search.daum.net/search?w=news&sort=recency&q={}&cluster=n&DA=PGD&dc=STC&pg=1&r=1&p={}&rc=1&at=more&sd={}&ed={}&period=u'.format(query, page, s_date, e_date)
    response = requests.get(url_search_result)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')   

    for atag in soup.find_all('a', {'class' : 'f_nb'}):
      links.append(atag['href'])
    
    if i%10 ==0:
      print(i-9, '-', i,  '번째 페이지의 기사 링크 모두 가져옴.')

  print('총', total_news, "개의 기사 중 'DAUM  뉴스'", len(links), '개 가져옴.')

  links = pd.DataFrame(links)
  links.columns = ['URLs']
  return links



print(  get_url_daum_news('육군', '2020-07-15', '2020-07-15'))
