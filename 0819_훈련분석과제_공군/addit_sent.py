import pandas as pd
import sqlite3
import NLP

con = sqlite3.connect("./training.db")

df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)

#sent score
NLP.add_sent_score(df_naver_news).to_sql('naver_news_0819_sent', con, if_exists = 'replace', index = False)
con.commit()



con.close()
