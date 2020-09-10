from kiwipiepy import Kiwi
import pickle
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
    naver_comment
"""

df_naver_news = pd.read_sql(query, con)
news = df_naver_news.content
word_count = scan_vocabulary(news, tokenize)

word_sorted = sorted(word_count, key = lambda k: word_count[k], reverse = True)
count_sorted = [word_count[k] for k in word_sorted]

fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

log_y = np.log(np.array(count_sorted))
log_x = np.log(np.arange(1, len(count_sorted)+1))

x_intercept = np.ones(len(count_sorted)).reshape(-1,1)
x_data = log_x.reshape(-1,1)
X = np.concatenate((x_intercept, x_data), axis = 1)
XtX = np.matmul(X.T, X)
XtX_inv = np.linalg.inv(XtX)
theta = np.matmul(XtX_inv, np.matmul(X.T, log_y))
a = np.exp(theta[0])
k = theta[1]

print('a = {}, k = {}'.format(a, k))
print(word_sorted[:50])
print(len(word_sorted))
ax1.plot(log_x, log_y)
grid_x = np.linspace(1, log_x[-1], 1000)
ax1.plot(grid_x, theta[0] + theta[1]  * grid_x )

ax2.plot(count_sorted)

plt.show()


