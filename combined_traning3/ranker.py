import textrank 
from textrank import textrank_keyword
import sqlite3
import pandas as pd
import pickle

con = sqlite3.connect("./training.db")
cur = con.cursor()

# del_query = "DELETE FROM naver_news WHERE time_written = '2020.08.15'"
# cur.execute(del_query)
# con.commit()

df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)
df_naver_news_comment = pd.read_sql('SELECT * FROM naver_comment', con)
con.close()

print(df_naver_news[['doc_id', 'title', 'time_written', 'content']].tail(10))
print(df_naver_news_comment[['title', 'time_written', 'content']].tail(10))




# #대표기사
# con = sqlite3.connect("./training.db")
# query = 'SELECT * FROM (SELECT ROW_NUMBER () OVER ( PARTITION BY time  ORDER BY n_comments DESC) RowNum, press, title, time, n_comments FROM naver_news) WHERE RowNum = 1 OR RowNum = 2'
# df_naver_news_rep = pd.read_sql(query, con)
# con.close()
# print(df_naver_news_rep)



# #대표댓글
# con = sqlite3.connect("./training.db")
# query = 'SELECT * FROM (SELECT ROW_NUMBER () OVER ( PARTITION BY time  ORDER BY n_comments DESC) RowNum, press, title, time, n_comments FROM naver_news) WHERE RowNum = 1 OR RowNum = 2'
# df_naver_news_rep = pd.read_sql(query, con)
# con.close()
# print(df_naver_news_rep)

#  10개 연관어
# keyword_total_news = textrank_keyword(df_naver_news.title, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
# print('전체 뉴스 제목', list(map(lambda x: x[0], keyword_total_news)))

# keyword_total_news = textrank_keyword(df_naver_news.content, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
# print('전체 뉴스 내용', list(map(lambda x: x[0], keyword_total_news)))

# keyword_total_news = textrank_keyword(df_naver_news[df_naver_news.time == '2020.06.22'].title, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
# print('6월 22일 뉴스 제목', list(map(lambda x: x[0], keyword_total_news)))

# keyword_total_news = textrank_keyword(df_naver_news_comment.content, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
# print('전체 뉴스 댓글', list(map(lambda x: x[0], keyword_total_news)))