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
"""


news_df_raw = pd.read_sql(query_select_title, con)
news_df_raw_grouped = news_df_raw.groupby('date')

text = news_df_raw.iloc[2, :].content
print(textrank.tokenize(text))