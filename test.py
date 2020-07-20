import crawl

import sqlite3
import pandas as pd
from kiwipiepy import Kiwi
import json
import pickle
from sklearn.feature_extraction.text import CountVectorizer

import operator
import numpy as np

#import stopwords
with open('./korean_stopwords.txt', 'rb') as f:
    stopwords = pickle.load(f)
stopwords = set(stopwords)


#prepare tokenizer
kiwi = Kiwi()
kiwi.prepare()

def tokenize(sent):
    res, score = kiwi.analyze(sent)[0] # 첫번째 결과를 사용
    return [word + ('다' if tag.startswith('V') else '') # 동사에는 '다'를 붙여줌
            for word, tag, _, _ in res
            if not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S') and word not in stopwords] # 조사, 어미, 특수기호는 제거

mycrawl = crawl.naver_crawl('육군', '2020.07.17')
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
    df = df.append(pd.Series([top_title, int(news_num) , top_words]), ignore_index=True)
df.columns = ['제목', '기사갯수', '단어']
df = df.sort_values(by = '기사갯수', desc = True)
print(df)