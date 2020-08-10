import textrank 
from textrank import textrank_keyword
import sqlite3
import pandas as pd
import pickle

con = sqlite3.connect("./training.db")
df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)
con.close()

naver_news_title = df_naver_news.title

aa = textrank_keyword(naver_news_title, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
print(aa)