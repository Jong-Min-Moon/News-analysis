import textrank 
from textrank import textrank_keyword
import sqlite3
import pandas as pd
import pickle

con = sqlite3.connect("./training.db")
cur = con.cursor()

############################################
#지우기
query_del = """
DELETE
FROM naver_news
WHERE query = '공군 특혜'
"""

cur.execute(query_del)
con.commit()


# #just read
# df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)
# #df_naver_news_comment = pd.read_sql('SELECT * FROM naver_comment2', con)
# print(df_naver_news)
# #print(df_naver_news_comment)


#############################################
# #N COMMENTS PARSED 확인
# query = 'SELECT * from naver_comment_parsed'
# df = pd.read_sql(query, con)
# print(df)

##############################################

# #날짜별 댓글 갯수
# query ="""
# SELECT crawldate, sum(n_comments)
# FROM naver_comment_parsed
# GROUP BY crawldate
# """ 
# df = pd.read_sql(query, con)
# print(df)
# df.to_csv('백선엽댓글카운트.csv')

####################################
# #댓글감성현황
# query = """
# SELECT
#     substr(time_written, 0, 12) as date,
#     sum(sent_score>0) as pos,
#     sum(sent_score<0) as neg,
#     sum(sent_score=0) as neu,
#     count(*) as total
# FROM naver_comment_BSY_sent
# GROUP BY substr(time_written, 0, 12)
# """
# df = pd.read_sql(query, con)
# print(df)
# df.to_csv('백선엽_댓글감성.csv', encoding = 'cp949')

####################################
# #뉴스감성현황
# query = """
# SELECT
#     substr(time_written, 0, 11) as date,
#     sum(sent_score>0) as pos,
#     sum(sent_score<0) as neg,
#     sum(sent_score=0) as neu,
#     count(*) as total
# FROM naver_news_BSY_sent
# GROUP BY substr(time_written, 0, 11)
# """
# df = pd.read_sql(query, con)
# print(df)
# df.to_csv('백선엽_뉴스감성.csv', encoding = 'cp949')
####################################

#뉴스 오전 오후 나누기

# query1 = """
# SELECT date,  sum(am) as sum_am, sum(pm)as sum_pm
# FROM (
#     SELECT
#         press,
#         title,
#         substr(time_written, 0, 11) as date,
#         substr(time_written, 12, 5) as time,
#         cast(substr(time_written, 12, 2) as integer) < 12  as am,
#         cast(substr(time_written, 12, 2) as integer) >=12 as pm,
#         sent_score
#     FROM naver_news_BSY_sent
#     WHERE length(time_written) > 11
# )
# GROUP BY date
# """
# df_naver_news = pd.read_sql(query1, con)
# print(df_naver_news)
# df_naver_news.to_csv('백선엽_시간단위_뉴스.csv', encoding = 'cp949')

################################################

# 댓글 오전 오후 나누기

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
#     FROM naver_comment_BSY_sent
#     WHERE length(time_written) > 13
#     )
# GROUP BY date
# """

# df = pd.read_sql(query, con)
# print(df)
# df.to_csv('백선엽_시간단위_댓글.csv', encoding = 'cp949')





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



##count table 만들기
# query5 = 'SELECT count(title), sum(n_comments) from naver_news_final_sent GROUP BY time_written'
# df5 = pd.read_sql(query5, con)
# df5.to_csv('공군카운트.csv')


# query3 = 'SELECT substr(time_written, 0, 11) as time_writ, sum(sent_score>0) as pos, sum(sent_score<0) as neg, sum(sent_score=0) as neu, count(*) as total FROM naver_comment_final_sent GROUP BY substr(time_written, 0, 11)'

# df1 = pd.read_sql(query3, con)
# df1.to_csv('공군댓글감성.csv')

# query4 = 'SELECT substr(time_written, 0, 11) as time_writ, sum(sent_score>0) as pos, sum(sent_score<0) as neg, sum(sent_score=0) as neu, count(*) as total FROM naver_news_final_sent GROUP BY substr(time_written, 0, 11)'

# df2 = pd.read_sql(query4, con)
# df2.to_csv('공군뉴스감성.csv')