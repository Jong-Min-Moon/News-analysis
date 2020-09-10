import crawl
import NLP

import sqlite3
import pandas as pd
from kiwipiepy import Kiwi
import json
import pickle
import sqlite3
import numpy as np




con = sqlite3.connect("./training.db")


query = """
SELECT
    substr(time_written, 0, 11) as time_written,
    press, title, in_url, query
FROM
    naver_news
"""
df_naver_news = pd.read_sql(query, con)
print(df_naver_news)
crawl.get_naver_news_comment(df_naver_news)
