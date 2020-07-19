import crawl
import sqlite3
import pandas as pd


mycrawl = crawl.naver_crawl('육군', '2020.07.17')
mycrawl.get_naver_news()
print(mycrawl.df_naver_news)