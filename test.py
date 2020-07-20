import crawl

import sqlite3
import pandas as pd


mycrawl = crawl.naver_crawl('육군', '2020.07.17')
mycrawl.get_naver_news()
print(mycrawl.df_naver_news)

related = mycrawl.df_naver_news[mycrawl.df_naver_news.is_relation == True]

related_groupby = related.groupby('master') #pd generic groupby. 뒤에 .mean() 등을 붙이면 일반적인 groupby가 됨.

for i, grp in related_groupby:
    print(grp)