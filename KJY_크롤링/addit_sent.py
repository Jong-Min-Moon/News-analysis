import pandas as pd
import sqlite3
import NLP

con = sqlite3.connect("./training.db")

df_naver_news = pd.read_sql('SELECT * FROM naver_news', con)
df_naver_news_comment = pd.read_sql('SELECT * FROM naver_comment2', con)

#sent score
NLP.add_sent_score(df_naver_news).to_sql('naver_news_BSY_sent', con, if_exists = 'replace', index = False)

NLP.add_sent_score(df_naver_news_comment).to_sql('naver_comment_BSY_sent', con, if_exists = 'replace', index = False)

con.commit()



con.close()
