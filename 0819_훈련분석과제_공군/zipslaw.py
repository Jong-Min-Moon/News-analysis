from kiwipiepy import Kiwi
import pickle
import sqlite3
import pandas as pd
#prepare tokenizer
kiwi = Kiwi()
kiwi.prepare()



#import stopwords
with open('./korean_stopwords.txt', 'rb') as f:
	stopwords = pickle.load(f)
stopwords = set(stopwords)

def tokenize(sent):
    res, score = kiwi.analyze(sent)[0] # 첫번째 결과를 사용
    return [word + ('다' if tag.startswith('V') else '') # 동사에는 '다'를 붙여줌
            for word, tag, _, _ in res
            if not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S') and word not in stopwords and len(word) > 1] # 조사, 어미, 특수기호는 제거

#and c<=int(len(sents)*max_count)
#, min_count=1, max_count = 0.6)
# if c >= min_count 
from collections import Counter

def scan_vocabulary(sents, tokenize):
    counter = Counter(w for sent in sents for w in tokenize(sent) ) 
    counter = {w:c for w,c in counter.items()}#횟수(c)가 min count 이상인 것만 골라서 word:occurence 딕셔너리를 만든다
    return counter

con = sqlite3.connect("./training.db")


query = """
SELECT *
FROM
    naver_news
"""

df_naver_news = pd.read_sql(query, con)
news = df_naver_news.content
word_count = scan_vocabulary(news, tokenize)
print(type(word_count))

print(word_count)