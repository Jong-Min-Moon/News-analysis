import textrank 
from textrank import textrank_keyword
import sqlite3
import pandas as pd
import pickle

con = sqlite3.connect("./training.db")
#query = 'UPDATE naver_comment SET doc_id = NULL'
#query = 'UPDATE naver_comment SET doc_id = (SELECT doc_id FROM naver_news WHERE in_url = naver_comment.url) WHERE doc_id IS NULL'  
query = 'UPDATE naver_news SET n_comments = (SELECT count(content) FROM naver_comment WHERE in_url = naver_comment.url)'  
cs = con.execute(query)
print(f'{cs.rowcount} rows are updated.')
con.commit()
con.close()