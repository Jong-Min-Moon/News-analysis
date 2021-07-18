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
SELECT * FROM naver_comment
"""
df_naver_comment = pd.read_sql(query, con)
print(df_naver_comment)
df_naver_comment_sent = NLP.add_sent_score(df_naver_comment)
con = sqlite3.connect("./rokanews.db")
df_naver_comment_sent.to_sql('naver_comment_sent', con, if_exists = 'append', index = False)