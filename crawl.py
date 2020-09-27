#진짜 날짜기능 추가 버전.
import pandas as pd 
import numpy as np

import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver  # selenium 프레임 워크에서 webdriver 가져오기

from sklearn.feature_extraction.text import CountVectorizer


from kiwipiepy import Kiwi

import operator

import json
import datetime
import time

import re #정규식
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제
import urllib.request        
import sys
import sqlite3

from random import uniform
import math #반올림



import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제
import pickle
# tokenize 함수를 정의합니다. 한국어 문장을 입력하면 형태소 단위로 분리하고, 
# 불용어 및 특수 문자 등을 제거한 뒤, list로 반환합니다.
#prepare tokenizer
kiwi = Kiwi()
kiwi.prepare()

def tokenize(sent):
    res, score = kiwi.analyze(sent)[0] # 첫번째 결과를 사용
    return [word + ('다' if tag.startswith('V') else '') # 동사에는 '다'를 붙여줌
            for word, tag, _, _ in res
            if not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S') and not tag.startswith('V')] # 조사, 어미, 특수기호는 제거


def daily_crawl_naver_news_by_keyword(today):
    mycrawl = naver_crawl('육군', today)
    mycrawl.get_naver_news()

    related = mycrawl.df_naver_news[mycrawl.df_naver_news.is_relation == True]
    related_groupby = related.groupby('master') #pd generic groupby. 뒤에 .mean() 등을 붙이면 일반적인 groupby가 됨.

    df = pd.DataFrame()
    for i, grp in related_groupby: #각 grp는 하나의 데이터프레임
        texts = grp.title
        top_title = texts.iloc[0]
        texts_for_CVT = [' '.join(tokenize(text)) for text in texts]
        cv = CountVectorizer(analyzer='word',       
                                token_pattern = '[가-힣]{2,}',  # num chars > 3
                                )
        tdm = cv.fit_transform(texts_for_CVT)
        words = cv.get_feature_names()
        count_mat = tdm.sum(axis=0)
        count = np.squeeze(np.asarray(count_mat))
        word_count = list(zip(words, count))
        word_count = sorted(word_count, key=operator.itemgetter(1), reverse=True)
        
        top_words = [word[0] for word in word_count[:2]]
        query_words = '육군, ' + ', '.join(top_words)
        print(query_words)
        news_num = mycrawl.get_news_num(query_words)
        df = df.append(pd.Series([top_title, news_num]), ignore_index=True)
    df.columns = ['title', 'num']
    df['time_written'] = today
    df = df.sort_values(by = 'num', ascending = False)
    print(df)
    return(df)


    
class naver_crawl():
    def __init__(self, query, crawldate):
        self.query = query
        self.crawldate = crawldate
        self.df_naver_news = pd.DataFrame(columns = ['doc_id', 'press', 'title', 'ex_url', 'in_url', 'content', 'is_relation', 'master', 'time_written'])

    def three_digits(self, num):
        numstring = str(num)
        #print(numstring)
        return self.query + self.crawldate.replace('.', '') + ''.join(list(np.zeros(4 - len(numstring), dtype = int).astype('str'))) + numstring

    def get_news_num(self, new_query):
        base_url = 'https://search.naver.com/search.naver'
        d = {'where':'news', 
             'query' : new_query,
             'sort':1,
             'photo':0,
             'field':1,
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
                        
        return int(total_news)

    def insert_naver_news(self, data):

            self.df_naver_news = self.df_naver_news.append(
                pd.DataFrame([data + [self.crawldate]],
                columns = ['doc_id', 'press', 'title', 'ex_url', 'in_url', 'content', 'is_relation', 'master', 'time_written']
                ),
                ignore_index = True)

 
    def get_naver_news(self):   
        

        #1. 탐색할 페이지 수 결정하기
        
        base_url = 'https://search.naver.com/search.naver'
        d = {'where':'news', 
             'query' : self.query,
             'sort':0,
             'photo':0,
             'field':1,
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
                    in_url_n = 'https://n.news.naver.com/article/{}/{}'.format(oid, aid) 
                    response_content = requests.get(in_url_n, headers={'User-Agent':'Mozilla/5.0'})
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
                    #print('관련 기사가 존재 x')
                    is_relation = False
                    #print(title)
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
                        #print('관련 기사가 5건 미만')
                        self.insert_naver_news([ #원본 기사를 일단 데이터프레임에 집어넣음
                            self.three_digits(doc_id), press, title, ex_url, in_url, content, is_relation, self.three_digits(doc_id)
                            ])
                        #print(title)
                        
                        litags_relation = relation.select('li')
                        num_litags_relation = len(litags_relation)
                        for k in range(num_litags_relation):
                            doc_id += 1
                            litag_relation = litags_relation[k]
                            title_sec = litag_relation.select('a')[0]['title']
                            #print(title_sec)
                            ex_url_sec = litag_relation.select('a')[0]['href']
                            press_sec = litag_relation.select('span.txt_sinfo > span.press')[0]['title']
                            self.insert_naver_news([
                                self.three_digits(doc_id), press_sec, title_sec, ex_url_sec, '',  '', True, self.three_digits(doc_id_og)
                        ])
                   
                            
                if is_more:
                    #print('관련 기사가 5건 이상, 총 {}건'.format(num_child))

                    
                    #관련뉴스의 페이지 수 가져오기
                    total_pages_more = math.ceil(num_child/10) # 검색 결과 페이지 수 계산. 이 개수만큼 for문을 돌려서 각 페이지의 뉴스기사 주소를 다 긁어올 것임.            
                    #print('총 {}페이지'.format(total_pages_more))
                   

                    for p in range(total_pages_more):
                        d_more = {'where':'news', 
                                'query' : self.query,
                                'sort':0,
                                'photo':0,
                                'field':1,
                                'reporter_article':'',
                                'pd': 3,
                                'ds' : self.crawldate,
                                'de' : self.crawldate,
                                'docid': news_more,
                                'refresh_start': 0,
                                'related' : 1}
                        d_more['start'] = str(p * 10 + 1) # 1, 11, 21, 31, ...
                        response_more = requests.get(base_url, params = d_more)
                        #print(response_more.url)
                        soup_more = BeautifulSoup(response_more.text, 'lxml')                            
                        litags_more = soup_more.select('ul.type01 > li')
                    
                    
                        n_litags_more = len(litags_more)
                        for m in range(n_litags_more):
                            litag_more = litags_more[m]                
                            #1. dt태그에서 기사 제목 뽑아내기
                            dt_tag = litag_more.select('dl > dt > a')[0]
                            title = dt_tag['title']
                            #print(title)
                            ex_url = dt_tag['href']
                            press = litag_more.select('dl > dd.txt_inline > span._sp_each_source')[0].text.replace('언론사 선정', '')
                                    
                            #2. '네이버 뉴스' 처리
                            in_url = ''

                            try: #'네이버 뉴스' 링크가 있는 경우에는 in_url이 업데이트된다. 내용도 가져온다.
                                in_url = litag_more.select('dl > dd.txt_inline > a')[0]['href']     
                                oid = in_url.split('&')[-2][4:]
                                aid = in_url.split('&')[-1][4:]
                                in_url_n = 'https://n.news.naver.com/article/{}/{}'.format(oid, aid) 
                                response_content = requests.get(in_url_n, headers={'User-Agent':'Mozilla/5.0'})
                                soup_content = BeautifulSoup(response_content.text, 'lxml')
                                news_area = soup_content.select('div#dic_area')
                                content = news_area[0].text

                                time_written_area = soup_content.select('div.media_end_head_info_datestamp_bunch > span.media_end_head_info_datestamp_time') # 검색 결과 개수 가져오기
                                time_written_parsed = time_written_area[0]['data-date-time']#0은 입력시간, 1은 최종수정시간
                            except:# '네이버 뉴스'링크가 없거나, 링크가 있어도 내용을 가져오지 못하는 경우.
                                content = ''
                                time_written_parsed = self.crawldate

                            self.df_naver_news = self.df_naver_news.append(
                                pd.DataFrame([[self.three_digits(doc_id), press, title, ex_url, in_url,  content, True, self.three_digits(doc_id_og), time_written_parsed]],
                                columns = ['doc_id', 'press', 'title', 'ex_url', 'in_url', 'content', 'is_relation', 'master', 'time_written']
                                        ),
                                ignore_index = True)
        
                                
                              
                            if m < n_litags_more - 1:
                                doc_id += 1
                            
 
  
            
            print('{}, {}th page'.format(self.crawldate, j))
                            
                
        print(len(self.df_naver_news.index)) 
        self.df_naver_news['v1'] = np.arange(len(self.df_naver_news.index))
        self.df_naver_news = self.df_naver_news.drop_duplicates(['ex_url'])
        self.df_naver_news = self.df_naver_news.drop_duplicates(['doc_id'])
        self.df_naver_news = self.df_naver_news.drop('v1', axis = 1)

        self.df_naver_news['query'] = self.query
        print(self.df_naver_news[['title', 'content']])
        print('{}: 총 {}개의 기사 가져옴'.format(self.crawldate,  len(self.df_naver_news.index)))
        
        #start database
        con = sqlite3.connect("./rokanews.db")
        self.df_naver_news.to_sql('naver_news', con, if_exists = 'append', index = False)
        con.commit()
        con.close()

        return self.df_naver_news


def get_naver_news_comment(df_naver_news):
    con = sqlite3.connect("./rokanews.db")

    urls_table = df_naver_news
    urls_table = urls_table[urls_table.in_url != '' ]
    urls_table = urls_table[~urls_table.in_url.str.contains("entertain")]
    urls_table = urls_table[~urls_table.in_url.str.contains("sports")]

    print('로드:', urls_table)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #browser = webdriver.Chrome('./chromedriver',options=chrome_options) #리눅스
    browser = webdriver.Chrome('./chromedriver_84_win.exe',options=chrome_options) #put this line inside the function def, or chrome winodws keeps opening
    
    df_ncomments = pd.DataFrame()

    print('로드 완료', urls_table)
    total_comments = 0
    for i, row in urls_table.iterrows():
        df = pd.DataFrame(columns=['press', 'title', 'url', 'content', 'like', 'dislike', 'time_written', 're_reply' ])

        doc_id = urls_table.loc[i, 'doc_id']
        press = urls_table.loc[i, 'press']
        title = urls_table.loc[i, 'title']
        url = urls_table.loc[i, 'in_url']
        query = urls_table.loc[i, 'query']
        crawldate = urls_table.loc[i, 'time_written']
        rep_url = '{}&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability'.format(url)    
        print(i, 'th news:', rep_url)
        browser.implicitly_wait(30) #웹 드라이버
        browser.get(rep_url)
        comment_page_num = 1
        #더보기 계속 클릭하기
        while True:
        #for _ in range(5): 
            try:
                see_more_button = browser.find_element_by_css_selector('a.u_cbox_btn_more')
                see_more_button.click()
                print('댓글 %d 페이지' % comment_page_num)     
                time.sleep(1)
                comment_page_num += 1
            except:
                print('버튼 없음')
                break
        
        #댓글추출
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        n_com_tags = soup.select('span.u_cbox_count')
        try:
            n_com = n_com_tags[0].text
        except:
            continue
        print('댓글 개수:', n_com)
        df_ncomments
        df_ncomments = df_ncomments.append(pd.Series([url, n_com, crawldate]), ignore_index=True)


        df_naver_news[df_naver_news.in_url == url]
        litags = soup.select('div.u_cbox_comment_box > div.u_cbox_area')
        if len(litags)>0: 
            for litag in litags:
                try:
                    content = litag.select('div.u_cbox_text_wrap > span.u_cbox_contents')[0].text   #댓글
                except:
                    content = 0
                if content != 0:
                    like = litag.select('div.u_cbox_tool > div.u_cbox_recomm_set > a')[0].select('em.u_cbox_cnt_recomm')[0].text #추천 
                    dislike = litag.select('div.u_cbox_tool > div.u_cbox_recomm_set > a')[1].select('em.u_cbox_cnt_unrecomm')[0].text #비추천
                    time_written = litag.select('div.u_cbox_info_base > span.u_cbox_date')[0].text #댓글작성날짜
                    re_reply = litag.select('div.u_cbox_tool > a.u_cbox_btn_reply > span.u_cbox_reply_cnt')[0].text #답글수

                    df = df.append(pd.DataFrame([[doc_id, query, press, title, url, content, like, dislike, time_written, re_reply]], columns=['query', 'press', 'title', 'url', 'content', 'like', 'dislike', 'time_written', 're_reply' ]), ignore_index=True)
        
        df.to_sql('naver_comment', con, if_exists = 'append', index = False)
        con.commit()
        
        total_comments += len(df)
    browser.quit() 
    
    #start database

    df_ncomments.columns = ['in_url', 'n_comments', 'crawldate']
    df_ncomments.to_sql('naver_comment_parsed', con, if_exists = 'append', index = False)
    con.commit()
    con.close()
    print('총 {}개의 기사에서 {}개의 댓글을 가져옴'.format( len(urls_table), total_comments ) )  
