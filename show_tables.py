import sqlite3
import pandas
import pandas as pd

con = sqlite3.connect("./rokanews.db")
mycur = con.cursor()
mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
available_table = (mycur.fetchall())
print(available_table)

data = pd.read_sql('SELECT * FROM pagerank', con)
print(data)

data = pd.read_sql('SELECT * FROM naver_comment_sent', con)
print(data)
print(data.columns)