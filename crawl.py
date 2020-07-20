import pandas as pd 
import numpy as np

import requests
from bs4 import BeautifulSoup



from kiwipiepy import Kiwi

import matplotlib.colors as mcolors

import json
import datetime
import time
from time import sleep
import re #정규식
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제
import urllib.request        
import sys

from random import uniform
import math #반올림



import datetime
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제
import pickle
# tokenize 함수를 정의합니다. 한국어 문장을 입력하면 형태소 단위로 분리하고, 
# 불용어 및 특수 문자 등을 제거한 뒤, list로 반환합니다.





    
class naver_crawl():
    def __init__(self, query, crawldate):
        self.query = query
        self.crawldate = crawldate
        self.df_naver_news = pd.DataFrame(columns = ['doc_id', 'press', 'title', 'ex_url', 'in_url', 'content', 'is_relation', 'master'])

    def three_digits(self, num):
        numstring = str(num)
        return self.crawldate.replace('.', '') + ''.join(list(np.zeros(3 - len(numstring), dtype = int).astype('str'))) + numstring

    def insert_naver_news(self, data):
            self.df_naver_news = self.df_naver_news.append(
                pd.DataFrame([data],
                columns = ['doc_id', 'press', 'title', 'ex_url', 'in_url', 'content', 'is_relation', 'master']
                ),
                ignore_index = True)

    def get_news_num(self, new_query):
        base_url = 'https://search.naver.com/search.naver'
        d = {'where':'news', 
             'query' : new_query,
             'sort':0,
             'photo':0,
             'field':0,
             'reporter_article':'',
             'pd': 3,
             'ds' : self.crawldate,
             'de' : self.crawldate,
             'docid':'',
             'refresh_start': 0,
             'start' :  1 }
        
        response = requests.get(base_url, params=d)
                
        # 네이버 기사 개수 가져오기
        soup = BeautifulSoup(response.text, 'lxml')

        total_news = soup.find('div', 'title_desc') # 검색 결과 개수 가져오기
        if isinstance(total_news , type(None)):
            return None #검색 결과가 아예 없으면 여기서 끝. 임시파일도 생성x. 뉴스는 있는데 네이버 뉴스만 있으면 빈 임시파일이 생성됨.
        else:
            total_news = re.split(' / ', total_news.text)[1][0:-1] # 1-10 / 629건 과 같은 형식에서 629만 가져오기. '/'로 쪼갠 다음, '건'을 지운다.
            total_news = int(total_news.replace(',','')) # 나눗셈을 하기 위해 자릿수 표시하는 ','를 지우고, string을 int로 변경
                        
        return total_news

    def get_naver_news(self):   
        #1. 탐색할 페이지 수 결정하기
        
        base_url = 'https://search.naver.com/search.naver'
        d = {'where':'news', 
             'query' : self.query,
             'sort':0,
             'photo':0,
             'field':0,
             'reporter_article':'',
             'pd': 3,
             'ds' : self.crawldate,
             'de' : self.crawldate,
             'docid':'',
             'refresh_start': 0,
             'start' :  1 }
        
        response = requests.get(base_url, params=d)
                
        # 네이버 기사 개수 가져오기
        soup = BeautifulSoup(response.text, 'lxml')

        total_news = soup.find('div', 'title_desc') # 검색 결과 개수 가져오기
        if isinstance(total_news , type(None)):
            return None #검색 결과가 아예 없으면 여기서 끝. 임시파일도 생성x. 뉴스는 있는데 네이버 뉴스만 있으면 빈 임시파일이 생성됨.
        else:
            total_news = re.split(' / ', total_news.text)[1][0:-1] # 1-10 / 629건 과 같은 형식에서 629만 가져오기. '/'로 쪼갠 다음, '건'을 지운다.
            total_news = int(total_news.replace(',','')) # 나눗셈을 하기 위해 자릿수 표시하는 ','를 지우고, string을 int로 변경
                        
        total_pages = math.ceil(total_news/10) # 검색 결과 페이지 수 계산. 이 개수만큼 for문을 돌려서 각 페이지의 뉴스기사 주소를 다 긁어올 것임.    
        print('pages:', total_pages) # 검색 결과 페이지 수 출력
        print('{} 총 {}페이지, {}개의 기사'.format( self.crawldate, total_pages, total_news) ) # 뉴스 개수 출력            
                        
        #2. 링크 추출
        doc_id = 0
        for j in range(total_pages):
            d['start'] = str(j*10 + 1) # 1, 11, 21, 31, ...
            response = requests.get(base_url, params=d)
            soup = BeautifulSoup(response.text, 'lxml')                            
            litags= soup.select('ul.type01 > li')
            
            for litag in litags:
                doc_id += 1
                is_more = False
                #1. dt태그에서 기사 제목 뽑아내기
                dt_tag = litag.select('dl > dt > a')[0]
                title = dt_tag['title']
                ex_url = dt_tag['href']
                press = litag.select('dl > dd.txt_inline > span._sp_each_source')[0].text.replace('언론사 선정', '')
                                
                #2. '네이버 뉴스' 처리
                in_url = ''

                try: #'네이버 뉴스' 링크가 있는 경우에는 in_url이 업데이트된다. 내용도 가져온다.
                    in_url = litag.select('dl > dd.txt_inline > a')[0]['href']     
                    oid = in_url.split('&')[-2][4:]
                    aid = in_url.split('&')[-1][4:]
                    in_url = 'https://n.news.naver.com/article/{}/{}'.format(oid, aid) 
                    response_content = requests.get(in_url, headers={'User-Agent':'Mozilla/5.0'})
                    soup_content = BeautifulSoup(response_content.text, 'lxml')
                    news_area = soup_content.select('div#dic_area')
                    content = news_area[0].text
                except:# '네이버 뉴스'링크가 없거나, 링크가 있어도 내용을 가져오지 못하는 경우.
                    content = ''
    
                        

                #3. 관련 기사가 존재할 경우
                try:
                    relation = litag.select('dl > dd > ul.relation_lst')[0]
                    is_relation = True
  
                except IndexError: #관련 기사가 존재x
                    print('관련 기사가 존재 x')
                    is_relation = False
                    print(title)
                    self.insert_naver_news([ 
                        self.three_digits(doc_id), press, title, ex_url, in_url, content, is_relation, ''
                        ])  

                if is_relation:
                    doc_id_og = doc_id
                    try:
                        news_more = litag.select('dl > dd > div.newr_more > a')[0]['onclick'].split("'")[1]
                        num_child = int(litag.select('dl > dd > div.newr_more > a')[0].text.split(' ')[1][:-1])
                        is_more = True
 
                    
                    except IndexError:
                        print('관련 기사가 5건 미만')
                        self.insert_naver_news([ #원본 기사를 일단 데이터프레임에 집어넣음
                            self.three_digits(doc_id), press, title, ex_url, in_url, content, is_relation, self.three_digits(doc_id)
                            ])
                        print(title)
                        
                        litags_relation = relation.select('li')
                        num_litags_relation = len(litags_relation)
                        for k in range(num_litags_relation):
                            doc_id += 1
                            litag_relation = litags_relation[k]
                            title_sec = litag_relation.select('a')[0]['title']
                            print(title_sec)
                            ex_url_sec = litag_relation.select('a')[0]['href']
                            press_sec = litag_relation.select('span.txt_sinfo > span.press')[0]['title']
                            self.insert_naver_news([
                                self.three_digits(doc_id), press_sec, title_sec, ex_url_sec, '',  '', True, self.three_digits(doc_id_og)
                        ])
                   
                            
                if is_more:
                    print('관련 기사가 5건 이상, 총 {}건'.format(num_child))

                    
                    #관련뉴스의 페이지 수 가져오기
                    total_pages_more = math.ceil(num_child/10) # 검색 결과 페이지 수 계산. 이 개수만큼 for문을 돌려서 각 페이지의 뉴스기사 주소를 다 긁어올 것임.            
                    print('총 {}페이지'.format(total_pages_more))
                   

                    for p in range(total_pages_more):
                        d_more = {'where':'news', 
                                'query' : self.query,
                                'sort':0,
                                'photo':0,
                                'field':0,
                                'reporter_article':'',
                                'pd': 3,
                                'ds' : self.crawldate,
                                'de' : self.crawldate,
                                'docid': news_more,
                                'refresh_start': 0,
                                'related' : 1}
                        d_more['start'] = str(p * 10 + 1) # 1, 11, 21, 31, ...
                        response_more = requests.get(base_url, params = d_more)
                        print(response_more.url)
                        soup_more = BeautifulSoup(response_more.text, 'lxml')                            
                        litags_more = soup_more.select('ul.type01 > li')
                    
                    
                        n_litags_more = len(litags_more)
                        for m in range(n_litags_more):
                            litag_more = litags_more[m]                
                            #1. dt태그에서 기사 제목 뽑아내기
                            dt_tag = litag_more.select('dl > dt > a')[0]
                            title = dt_tag['title']
                            print(title)
                            ex_url = dt_tag['href']
                            press = litag_more.select('dl > dd.txt_inline > span._sp_each_source')[0].text.replace('언론사 선정', '')
                                    
                            #2. '네이버 뉴스' 처리
                            in_url = ''

                            try: #'네이버 뉴스' 링크가 있는 경우에는 in_url이 업데이트된다. 내용도 가져온다.
                                in_url = litag_more.select('dl > dd.txt_inline > a')[0]['href']     
                                oid = in_url.split('&')[-2][4:]
                                aid = in_url.split('&')[-1][4:]
                                in_url = 'https://n.news.naver.com/article/{}/{}'.format(oid, aid) 
                                response_content = requests.get(in_url, headers={'User-Agent':'Mozilla/5.0'})
                                soup_content = BeautifulSoup(response_content.text, 'lxml')
                                news_area = soup_content.select('div#dic_area')
                                content = news_area[0].text
                            except:# '네이버 뉴스'링크가 없거나, 링크가 있어도 내용을 가져오지 못하는 경우.
                                content = ''
                        
                            self.insert_naver_news([
                                self.three_digits(doc_id), press, title, ex_url, in_url,  content, True, self.three_digits(doc_id_og)
                                ])
                            if m < n_litags_more - 1:
                                doc_id += 1

 
  
            
            print('{}, {}th page'.format(self.crawldate, j))
                            
                
        print(len(self.df_naver_news.index)) 
        self.df_naver_news['time'] = self.crawldate
        self.df_naver_news['v1'] = np.arange(len(self.df_naver_news.index))
        self.df_naver_news = self.df_naver_news.drop_duplicates(['ex_url'])
        self.df_naver_news = self.df_naver_news.drop('v1', axis = 1)

        self.df_naver_news['n_comments'] = 0
    
        print('{}: 총 {}개의 기사 가져옴'.format(self.crawldate,  len(self.df_naver_news.index)))
        return self.df_naver_news