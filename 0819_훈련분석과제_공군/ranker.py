import textrank 
from textrank import textrank_keyword
import sqlite3
import pandas as pd
import pickle

con = sqlite3.connect("./training.db")
cur = con.cursor()


#지우기 
# query = """
# DELETE FROM naver_comment_final_sent
# WHERE query = '백선엽'
# """
# cs = cur.execute(query)
# print(f'{cs.rowcount} rows are updated.')
# con.commit()

#just read
# df_naver_news = pd.read_sql('SELECT * FROM naver_news_0819_sent', con)
# df_naver_news_comment = pd.read_sql('SELECT * FROM naver_comment_final_sent', con)
# print(len(df_naver_news_comment))
# print(df_naver_news[df_new_naver.content != ''][['doc_id', 'title', 'time_written', 'content']].head(10))
# print(df_naver_news_comment[['title', 'time_written', 'content']].tail(10))

#############################################

#뉴스 오전 오후 나누기

query1 = """
SELECT date,  sum(am) as sum_am, sum(pm)as sum_pm
FROM (
    SELECT
        press,
        title,
        substr(time_written, 0, 11) as date,
        substr(time_written, 12, 5) as time,
        cast(substr(time_written, 12, 2) as integer) < 12  as am,
        cast(substr(time_written, 12, 2) as integer) >=12 as pm,
        sent_score
    FROM naver_news_0819_sent
    WHERE length(time_written) > 11
)
GROUP BY date
"""
df_naver_news = pd.read_sql(query1, con)
print(df_naver_news)
df_naver_news.to_csv('공군_시간단위_뉴스.csv', encoding = 'cp949')

################################################

## 댓글 오전 오후 나누기

# query = """
# SELECT sum(pm) as sum_pm, sum(am) as sum_am, date
# FROM (
#     SELECT
#         title,
#         content,
#         substr(time_written, 0, 12) as date,
#         substr(time_written, 13, 5) as time,
#         cast(substr(time_written, 13, 2) as integer)>=12 as pm,
#         cast(substr(time_written, 13, 2) as integer)<12 as am,
#         sent_score
#     FROM naver_comment_final_sent
#     WHERE length(time_written) > 13
#     )
# GROUP BY date
# """

# df = pd.read_sql(query, con)
# print(df)
# df.to_csv('공군_시간단위_댓글.csv', encoding = 'cp949')

#중복제거
# query_distinct = """
# SELECT *
# FROM naver_news_0819_sent
# WHERE ex_url in (SELECT DISTINCT ex_url FROM naver_news_0819_sent)
# """

# df_naver_news = pd.read_sql(query_distinct, con)
# print(df_naver_news)


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