import numpy as np
import pandas as pd
import re
import gensim

import sqlite3


import pickle
import json
from kiwipiepy import Kiwi
import pickle

#prepare tokenizer
kiwi = Kiwi()
kiwi.prepare()

#import stopwords
with open('./korean_stopwords.txt', 'rb') as f:
    stopwords = pickle.load(f)

stopwords = set(stopwords)

def tokenize(sent):
    res, score = kiwi.analyze(sent)[0] # 첫번째 결과를 사용
    return [word + ('다' if tag.startswith('V') else '') # 동사에는 '다'를 붙여줌
            for word, tag, _, _ in res
            if len(word) > 1 and not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S') and word not in stopwords] # 조사, 어미, 특수기호는 제거



con = sqlite3.connect("./training.db")


#just read
df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)
df_naver_news_comment = pd.read_sql('SELECT * FROM naver_comment2', con)

comment_raw = df_naver_news_comment.content
news_text_raw =  df_naver_news.content
news_title_raw = df_naver_news.title

text_combined_raw = pd.concat([comment_raw, news_text_raw, news_title_raw], ignore_index = True)
tokens = map(tokenize, text_combined_raw)


from gensim.models import Word2Vec
embedding_model = Word2Vec(tokens, size = 100, window = 5, min_count = 20, workers = 2, iter = 120, sg = 1)
print(embedding_model.most_similar(positive = ['김정은'], topn = 50))
print(embedding_model.most_similar(positive = ['정은'], topn = 50))