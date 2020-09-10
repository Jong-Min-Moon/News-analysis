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

con = sqlite3.connect("./training.db")

query = "SELECT naver_news2.title, naver_news2.in_url, naver_news2.ex_url, naver_news2.press, naver_news2.title from naver_news2 left outer join naver_news on naver_news2.ex_url = naver_news.ex_url WHERE naver_news.ex_url is null"
urls_table = pd.read_sql(query, con)
urls_table = urls_table[urls_table.in_url != '' ]
print('로드:', urls_table)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
#browser = webdriver.Chrome('./chromedriver',options=chrome_options) #리눅스
browser = webdriver.Chrome('./chromedriver_84_win.exe',options=chrome_options) #put this line inside the function def, or chrome winodws keeps opening

print('로드 완료', urls_table)
total_comments = 0
df = pd.DataFrame(columns=['press', 'title', 'url', 'content', 'like', 'dislike', 'time_written', 're_reply' ])

for i, row in urls_table.iterrows():

    press = urls_table.loc[i, 'press']
    title = urls_table.loc[i, 'title']
    url = urls_table.loc[i, 'in_url']
    rep_url = '{}&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability'.format(url)    
    print(i, 'th news:', rep_url)
    browser.implicitly_wait(30) #웹 드라이버
    browser.get(rep_url)
    comment_page_num = 1
    #더보기 계속 클릭하기
    while True:
        
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

                df = df.append(pd.DataFrame([['공군 특혜', press, title, url, content, like, dislike, time_written, re_reply]], columns=['query', 'press', 'title', 'url', 'content', 'like', 'dislike', 'time_written', 're_reply' ]), ignore_index=True)
    total_comments += len(df)

    print(df)
    
df.to_csv('naver_comment2.csv', )
    
browser.quit() 
con.close()
print('총 {}개의 기사에서 {}개의 댓글을 가져옴'.format( len(urls_table), total_comments ) )    