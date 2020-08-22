import sqlite3
import pandas as pd
import textrank

con = sqlite3.connect("./training.db")
cur = con.cursor()

query_select = """
SELECT
    content,
    substr(time_written, 0, 12) as date
FROM
    naver_comment2
"""

comment_df_raw = pd.read_sql(query_select, con)

comment_df_raw_grpd = comment_df_raw.groupby('date') #pd generic groupby. 뒤에 .mean() 등을 붙이면 일반적인 groupby가 됨.

pagerank_keywords = pd.DataFrame()

for crawl_date, group in comment_df_raw_grpd:
    if crawl_date =='2020.05.09':
        break
    #  10개 연관어
    keyword_total_news = textrank.textrank_keyword(group.content, textrank.tokenize, min_count = 2, window = 4, min_cooccurrence = 2, df=0.85, max_iter=60, topk=20)
    print(keyword_total_news)
    #crawl_date, *list(map(lambda x: x[0], keyword_total_news)))