import sqlite3
import pandas as pd
import textrank

con = sqlite3.connect("./training.db")
cur = con.cursor()


query_select_title = """
SELECT
    content,
    substr(time_written, 0, 12) as date
FROM
    naver_news
WHERE
    length(time_written) > 11

"""


news_df_raw = pd.read_sql(query_select_title, con)
news_df_raw_grouped = news_df_raw.groupby('date')
news_df_raw_grouped
pagerank_keywords = pd.DataFrame()

for crawl_date, group in news_df_raw_grouped:
    print(crawl_date)
    if crawl_date =='2020.05.09' or crawl_date == '2020-04-14':
        break
    #  10개 연관어
    keyword_total_news = textrank.textrank_keyword(group.content, textrank.tokenize, min_count = 2, window = 5, min_cooccurrence = 2, df=0.85, max_iter=60, topk=50)
    # print(*list(map(lambda x: x[0], keyword_total_news)))
    print(keyword_total_news)