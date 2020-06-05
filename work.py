import pandas as pd 
import numpy as np
import scipy

import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver  # selenium 프레임 워크에서 webdriver 가져오기


import konlpy
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from kiwipiepy import Kiwi
import tomotopy as tp

from sklearn.manifold import TSNE
import matplotlib.colors as mcolors

import json
import datetime
import time
from time import sleep
import re #정규식
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import urllib.request        
import sys

from random import uniform
import math #반올림



import datetime
import os #파일 및 폴더 관리
import shutil #파일 한번에 삭제

# tokenize 함수를 정의합니다. 한국어 문장을 입력하면 형태소 단위로 분리하고, 
# 불용어 및 특수 문자 등을 제거한 뒤, list로 반환합니다.


kiwi = Kiwi()
print('kwi')
kiwi.prepare()

def tokenize(sent):
    res, score = kiwi.analyze(sent)[0] # 첫번째 결과를 사용
    return [word + ('다' if tag.startswith('V') else '') # 동사에는 '다'를 붙여줌
            for word, tag, _, _ in res
            if not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S')] # 조사, 어미, 특수기호는 제거

def merge(mypath):
    file_list = os.listdir(mypath)
    file_list.sort()

    data = pd.read_csv( mypath + '/' + file_list[0] )
    for filename in file_list[1:]:
        data = data.append(pd.read_csv(mypath + '/' + filename), ignore_index=True)
        print(filename)
    
    return(data)

def Do_LDA(df, n_topic, n_iter):
    df_with_tsne = df[df.content != 0].copy()
    texts = df_with_tsne.content
    model = tp.LDAModel(k = n_topic, alpha=0.1, eta=0.01, min_cf=5, min_df = 2,  tw=tp.TermWeight.PMI)
    for i, line in enumerate(texts):
        if line != []:
            token = tokenize(line)
            print(token)
            model.add_doc(token) # 공백 기준으로 단어를 나누어 model에 추가합니다.
        if line == []:
            df_with_tsne.drop([i])
        if i % 10 == 0: print('Document #{} has been loaded'.format(i))

    model.train(0) 
    print('Total docs:', len(model.docs))
    print('Total words:', model.num_words)
    print('Vocab size:', model.num_vocabs)
        
    # 다음 구문은 train을 총 200회 반복하면서, 
    # 매 단계별로 로그 가능도 값을 출력해줍니다.
    # 혹은 단순히 model.train(200)으로 200회 반복도 가능합니다.
    for i in range(n_iter):
        if i % 1000 ==0:
            print('Iteration {}\tLL per word: {}'.format(i, model.ll_per_word))
        model.train(1)
        
    # 학습된 토픽들을 출력해보도록 합시다.
    for i in range(model.k):
        # 토픽 개수가 총 20개이니, 0~19번까지의 토픽별 상위 단어 10개를 뽑아봅시다.
        res = model.get_topic_words(i, top_n=10)
        print('Topic #{}'.format(i), end='\t')
        print(', '.join(w for w, p in res))

    LDA_today = pd.DataFrame()
    print(df.time)
    today = df.time.iloc[0]

    for i in range(n_topic):
        topic = list(zip(model.vocabs, model.get_topic_word_dist(i)))
        topic.sort(key = lambda x: -x[1])
        topic = topic[:30]
        top3 = '/ '.join(item[0] for item in topic[:3])
       
        temp_series = topic + [today, str(i), top3]
        LDA_today = LDA_today.append(pd.Series(temp_series), ignore_index = True)

    LDA_today.columns = ['word{}'.format(i) for i in range(30)]+ ['time', 'label', 'top3']
    LDA_today.to_csv( 'D:/crawling/News-analysis/LDAs/LDA_{}.csv'.format(today),index=False, encoding='utf-8-sig')  
      

    #T-SNE 정보를 원본 데이터프레임에 추가
    # Get topic weights
    topic_weights = []
    for i, doc in enumerate(model.docs):
        topic_weights.append(np.array(model.infer( doc, iter=100, tolerance=-1, workers=0, parallel=0, together=False )[0]))

    # Array of topic weights    
    arr = pd.DataFrame(topic_weights).fillna(0).values

    # Dominant topic number in each doc
    label = np.argmax(arr, axis=1)

    # tSNE Dimension Reduction
    tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca')
    tsne_lda = tsne_model.fit_transform(arr)

    df_with_tsne['x'] = tsne_lda[:,0]
    df_with_tsne['y'] = tsne_lda[:,1]
    df_with_tsne['label'] = label
    
    top3_to_merge = LDA_today[['label', 'top3']].copy()
    top3_to_merge.label = top3_to_merge.label.astype('int64')
    df_with_tsne = pd.merge(df_with_tsne, top3_to_merge, on = 'label', how = 'left')
    df_with_tsne.to_csv('D:/crawling/News-analysis/NN/NN_{}.csv'.format(today),index=False, encoding='utf-8-sig')

    

class Crawler():
    def __init__(self, query, s_date, e_date, root):
        self.query = query
        self.d_range = ( pd.date_range(start = s_date, end = e_date) ).strftime("%Y.%m.%d").tolist()
        self.root = root
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

        self.NC_urls = list(np.repeat(0, len(self.d_range)))

        

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
            #print('{}페이지에는 {}개의 기사'.format( j+1, len(litags) ))
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
                        content = 0
                        
                    df = df.append(pd.DataFrame([[press, title, link, content]], columns=['press','title','url', 'content']), ignore_index=True)
             
            if j%10 ==0:
                print('{}, {}th page'.format(dt, j))
                            
                
                    
        df['time'] = dt
        df['v1'] = np.arange(len(df.index))
        df.drop_duplicates(['url'])
        df = df.drop('v1', axis = 1)
        self.NC_urls[i] =  df   
    
        df.to_csv( self.crawl_objs['NC'][2] +'/naver_comment_url{}_{}.csv'.format(self.query, dt),index=False)
        #df.to_csv( self.root +'/NC/naver_comment_url_{}_{}.csv'.format(self.query, dt),index=False)
        print('{}: 총 {}개의 기사 중 {}개의 네이버 기사(댓글 달기 가능)를 가져옴'.format(dt, total_news, len(df.index)))
        #self.NC_urls = df 
       

    def getNC(self, j):
        df = pd.DataFrame(columns=['press', 'title', 'url', 'content', 'like', 'dislike', 'time', 're_reply' ])
        print(j,'번째 날의 기사들의 댓글')
        urls_table = self.NC_urls[j]
        print('로드:', urls_table)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('../chromedriver.exe',options=chrome_options) #put this line inside the function def, or chrome winodws keeps opening

        print('로드 완료', urls_table)
        for i, row in urls_table.iterrows():
            print(i, 'th news')
            press = urls_table.loc[i, 'press']
            title = urls_table.loc[i, 'title']
            url = urls_table.loc[i, 'url']
            rep_url = '{}&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability'.format(url)    
            
            browser.implicitly_wait(4) #웹 드라이버
            browser.get(rep_url)
            
            #더보기 계속 클릭하기
            while True:
                try:
                    see_more_button = browser.find_element_by_css_selector('.u_cbox_page_more')
                    see_more_button.click()        
                    time.sleep(1)
                except:
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
                        time = litag.select('div.u_cbox_info_base > span.u_cbox_date')[0].text #댓글작성날짜
                        re_reply = litag.select('div.u_cbox_tool > a.u_cbox_btn_reply > span.u_cbox_reply_cnt')[0].text #답글수

                        df = df.append(pd.DataFrame([[press, title, url, content, like, dislike, time, re_reply]], columns=['press', 'title', 'url', 'content', 'like', 'dislike', 'time', 're_reply' ]), ignore_index=True)
            
        df.to_csv( self.crawl_objs['NC'][3] +'/naver_comment_{}_{}.csv'.format(self.query, self.d_range[j],index=False))
        self.NC = df
        print('총 {}개의 기사에서 {}개의 네이버 기사(댓글 달기 가능)를 가져옴'.format( len(urls_table), len(df) ) )
        browser.quit() 



def add_sent_score(data):
    from konlpy.tag import Okt
    new_data = data[data.content != 0].copy()
    docs = new_data.content
    n = len(docs)


    docs_brk = []
    for doc in docs:
        doc_brk = tokenize(doc)
        tknd = ' '.join( doc_brk )
        docs_brk.append(tknd)
    
    vect = CountVectorizer(min_df = 2, max_df = n * 0.7)
    vect.fit( docs_brk )

    #print("어휘 사전의 크기:", len(vect.vocabulary_))
   # print('어휘 사전의 내용:', vect.vocabulary_)
    BOW = vect.transform(docs_brk)
    word_list = list(vect.vocabulary_)

    with open('D:/crawling/KnuSentiLex-master/data/SentiWord_info.json', 'r', encoding='UTF8') as fileref:
        dict_str = fileref.read() 

    sent_dict = json.loads(dict_str) #감성어 사전


    #감성어 사전에 있는 단어만 극성점수 리스트 만들기
    word_scores = pd.DataFrame(columns = [ 'word', 'polar'])
    for i in range(len(word_list)):
        word = word_list[i]
        for sentword in sent_dict:
            if ( (word in sentword['word']) or (word in sentword['word_root']) ):
                word_scores.loc[i, 'word'] = word
                word_scores.loc[i, 'polar'] = int( sentword['polarity'] ) 
                #print(word)
                break

    #전체 단어 리스트에 left join하면 점수 없는 단어는 점수가 NA로 표시될 것
    word_list_pd = pd.DataFrame(word_list, columns = ['word'])
    score_vec = pd.merge(word_list_pd, word_scores, how = 'left', on='word')


    #Countvectorizer의 word index 순으로 정렬하기
    score_vec_fin = pd.DataFrame(columns = [ 'word', 'polar'])
    for i in score_vec.index:
        print(i)
        word = score_vec.loc[i,'word']
        idx = vect.vocabulary_[word]
        score_vec_fin.loc[idx, 'polar'] = score_vec.loc[i,'polar']
        score_vec_fin.loc[idx, 'word'] = word
    score_vec_fin.sort_index(inplace = True)

    #행렬 연산을 위해 변형
    score_vec_comp = score_vec_fin.polar.to_numpy().reshape(-1,1)

    #NaN을 0으로 바꿔주기
    score_vec_comp2 = np.repeat(0, len(score_vec_comp))
    for i in range( len(score_vec_comp) ):
        if not np.isnan( score_vec_comp[i][0] ):
            score_vec_comp2[i] = score_vec_comp[i][0]
    score_vec_comp2 = score_vec_comp2.reshape(-1,1)

    #감성점수 계산. BOW = 문서 * 단어, score_vec_comp = 단어 * 점수  --> 행렬-벡터 곱은 문서 * 점수
    r = scipy.sparse.csr_matrix.dot(BOW, score_vec_comp2)
    r = np.ndarray.flatten(r)
    tot = BOW.sum(axis=1)#문서당 단어 수
    tot = np.ndarray.flatten(np.asarray(tot))

    #np.count_nonzero(score_vec_comp3 == 1)
    #np.count_nonzero(r > 1)
    new_data['polar_sum'] = r
    new_data['tot'] = tot
    new_data['sent_score'] = new_data['polar_sum'] / new_data['tot']
    new_data['label'] = 'NA'
    return(new_data)



