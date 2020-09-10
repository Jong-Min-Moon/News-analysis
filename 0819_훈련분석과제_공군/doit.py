import pandas as pd
import sqlite3
import NLP

con = sqlite3.connect("./training.db")
cur = con.cursor()

##doc_id 연결
# query1 = """ 
# UPDATE naver_comment_final_sent
# SET doc_id = (
#     SELECT doc_id
#     FROM naver_news_0819_sent
#     WHERE in_url = naver_comment_final_sent.url)
# """
# cs = cur.execute(query1)
# print(f'{cs.rowcount} rows are updated.')
# con.commit()

##기사에 n_comments 붙이기
# query2 ="""
# UPDATE naver_news_0819_sent
# SET n_comments = (
#     SELECT count(content)
#     FROM naver_comment_final_sent
#     WHERE naver_comment_final_sent.doc_id = naver_news_0819_sent.doc_id
#     )
# """ 
# cs = cur.execute(query2)
# print(f'{cs.rowcount} rows are updated.')
# con.commit()

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

