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
    
with open('schema.sql') as fp:
    con.executescript(fp.read())
con.commit()
con.close()

mycrawl = crawl.naver_crawl('공군 황제', '2020.06.12')
mycrawl.get_naver_news()

crawl_daterange = pd.date_range('2020.06.13', '2020.08.13')
for crawl_date_obj in crawl_daterange:
    mycrawl = crawl.naver_crawl('공군 황제', crawl_date_obj.strftime('%Y.%m.%d'))
    mycrawl.get_naver_news()

crawl_daterange = pd.date_range('2020.06.12', '2020.08.13')
for crawl_date_obj in crawl_daterange:
    mycrawl = crawl.naver_crawl('공군 특혜', crawl_date_obj.strftime('%Y.%m.%d'))
    mycrawl.get_naver_news()
