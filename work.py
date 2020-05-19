import pandas as pd 
import numpy as np

import requests
from bs4 import BeautifulSoup

import datetime
import time
from time import sleep
import re #정규식
from tqdm import trange #
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import urllib.request        
import sys

from random import uniform
import math #반올림


import pandas as pd 
import datetime
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제



class Crawler():
    def __init__(self, query, s_date, e_date, root):
        self.query = query
        self.d_range = ( pd.date_range(start = s_date, end = e_date) ).strftime("%Y.%m.%d").tolist()
        self.path = root + '/crawl_{}_{}_{}'.format(query, s_date, e_date) #공통 디렉토리
        
        self.crawl_obj_list = ['NC', 'NB']
        self.crawl_objs = {}
        for crawl_obj in self.crawl_obj_list:
            templist = []
            templist.append( self.path + '/' + crawl_obj )
            templist.append( templist[0] + '/temp')
            templist.append( templist[1] + '/url')
            templist.append( templist[1] + '/data')
            self.crawl_objs[crawl_obj] = templist


    def mkpath(self):
        os.mkdir(self.path)
        for crawl_obj in self.crawl_objs:
            for pathname in self.crawl_objs[crawl_obj]:
                os.mkdir(pathname)


    def getNClinks(self, i):   
        dt = self.d_range[i]
        print(dt)

        #1. 탐색할 페이지 수 결정하기
        df = pd.DataFrame(columns=['press', 'title', 'url', 'content'])
        base_url = 'https://search.naver.com/search.naver'
        d = {'sort':1, 'photo':0, 'field':0, 'where':'news', 'reporter_article':'', 'pd':3, 'docid':'', 'refresh_start':0, 'mynews':0 }
        d['query'] = self.query
        d['ds'] = dt #ex. '2020.03.01'
        d['de'] = dt
        d['start'] = 1
        d['nso'] = 'so:dd,p:from{}to{},a:all'.format(dt, dt )

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
        print('{} 총 {}페이지, {}개의 기사'.format( dt, total_pages, total_news) ) # 뉴스 개수 출력            
                        
        #2. 링크 추출
        for j in range(total_pages):
            d['start'] = str(j*10 + 1) # 1, 11, 21, 31, ...
            response = requests.get(base_url, params=d)
            soup = BeautifulSoup(response.text, 'lxml')
                            
            litags = soup.select('ul.type01 > li')
            print('{}페이지에는 {}개의 기사'.format( j+1, len(litags) ))
            for litag in litags:
                try:
                    link = litag.select('dl > dd.txt_inline > a')[0]['href']
                except:
                    link = 0
                    #####
                if link != 0:
                    title = litag.select('dl > dt > a')[0]['title']
                    press = litag.select('dl > dd.txt_inline > span._sp_each_source')[0].text.replace('언론사 선정', '')
                        
                    oid = link.split('&')[-2][4:]
                    aid = link.split('&')[-1][4:]
                    n_url = 'https://n.news.naver.com/article/{}/{}'.format(oid, aid) 
                    response = requests.get(n_url, headers={'User-Agent':'Mozilla/5.0'})
                    soup = BeautifulSoup(response.text, 'lxml') 
                    try:
                        news_area = soup.select('div#dic_area')
                        content = news_area[0].text
                    except:
                        content = []
                        
                    df = df.append(pd.DataFrame([[press, title, link, content]], columns=['press','title','url', 'content']), ignore_index=True)
             
            if j%10 ==0:
                print('{}, {}th page'.format(dt, j))
                            
                
                    
        df['time'] = dt
        df['v1'] = np.arange(len(df.index))
        df.drop_duplicates(['url'])
        df = df.drop('v1', axis = 1)
        
        df.to_csv( self.crawl_objs['NC'][2] +'/naver_comment_url{}_{}.csv'.format(self.query, dt),index=False)
        print('{}: 총 {}개의 기사 중 {}개의 네이버 기사(댓글 달기 가능)를 가져옴'.format(dt, total_news, len(df.index)))
      

