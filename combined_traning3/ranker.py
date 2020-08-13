import textrank 
from textrank import textrank_keyword
import sqlite3
import pandas as pd
import pickle

con = sqlite3.connect("./training.db")
df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)
df_naver_news_comment = pd.read_sql('SELECT * FROM naver_comment', con)
con.close()

# print(df_naver_news[['title', 'n_comments']].head())

#groupby로 요일별 뉴스 및 댓글 갯수 세기
# df_naver_news_comment['date_written'] = df_naver_news_comment.time.str.slice(stop=10)
# df_naver_news_grp = df_naver_news.groupby('time')
# print('뉴스', df_naver_news_grp.count())

# df_naver_news_comment_grp = df_naver_news_comment.groupby('date_written')
# print('댓글', df_naver_news_comment_grp.count())


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

keyword_total_news = textrank_keyword(df_naver_news[df_naver_news.time == '2020.06.22'].title, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
print('6월 22일 뉴스 제목', list(map(lambda x: x[0], keyword_total_news)))

keyword_total_news = textrank_keyword(df_naver_news_comment.content, textrank.tokenize, min_count = 2, window = -1, min_cooccurrence = 2, df=0.85, max_iter=30, topk=10)
print('전체 뉴스 댓글', list(map(lambda x: x[0], keyword_total_news)))