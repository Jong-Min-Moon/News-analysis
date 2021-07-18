import crawl
import NLP

import sqlite3
import pandas as pd
from kiwipiepy import Kiwi
import json
import pickle
import sqlite3
import numpy as np




con = sqlite3.connect("./rokanews.db")


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

# 1차 중단
#"""
# 2083 th news: https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=100&oid=437&aid=0000236517&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability
# """

#2차 중단
# 3817 th news: https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=100&oid=018&aid=0004628709&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability

#3차 중단
#5489 th news: https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=104&oid=011&aid=0003732184&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability

#4차 중단
#푸틴, 김정은에 기념 메달 수여...'2차대전 승전 75주년'