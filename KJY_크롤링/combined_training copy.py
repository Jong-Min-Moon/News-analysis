import crawl
import NLP

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




def do_crawl(keyword, dt, initialize):
    #prepare database
    
    if initialize:
        con = sqlite3.connect("./training.db")
        with open('schema.sql') as fp:
            con.executescript(fp.read())
        con.commit()
        con.close()

    mycrawl = crawl.naver_crawl(keyword, dt)
    mycrawl.get_naver_news()
    #sent score
    # if len(mycrawl.df_naver_news_comment) > 5:
    #     NLP.add_sent_score(mycrawl.df_naver_news_comment).to_sql('naver_comment', con, if_exists = 'append', index = False)

    # con.commit()


#    # doc id를 join해서 붙임
#     query = 'UPDATE naver_comment SET doc_id = (SELECT doc_id FROM naver_news WHERE in_url = naver_comment.url) WHERE doc_id IS NULL'  
#     cs = con.execute(query)
#     print(f'{cs.rowcount} rows are updated.')
#     con.commit()


 
