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


from collections import Counter

def scan_vocabulary(sents, tokenize, min_count=2, max_count = 0.6):
    #모든 단어를 쭉 나열
	counter = Counter(w for sent in sents for w in tokenize(sent)) 
    
	#횟수(c)가 min count 이상인 것만 골라서 word:occurence 딕셔너리를 만든다
	counter = {w:c for w,c in counter.items() if c >= min_count and c<=int(len(sents)*max_count)}

	#bag of words로 문서를 표현하는 방법은 t2d mat와  id2word/word2id dict가 있음.
	#그 중 후자를 선택.
	#sorted로 list comprehension할 수 있음. key에 음수 붙이면 내림차순.
	idx_to_vocab = [ w for w, _ in sorted(counter.items(), key=lambda x:-x[1]) ]
	vocab_to_idx = {vocab:idx for idx, vocab in enumerate(idx_to_vocab)}
	return idx_to_vocab, vocab_to_idx

from collections import defaultdict

def cooccurrence(tokens, vocab_to_idx, window = 2, min_cooccurrence=2):
    counter = defaultdict(int)
    for s, tokens_i in enumerate(tokens):
				#tokens에서 단어장에 있는 단어만 꺼내서 idx만 기록한다. 토큰이 [1,3,10]같은 형태가 된다
        vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
        n = len(vocabs) #vocabs는 문장 하나이다. n = 문장의 길이
        for i, v in enumerate(vocabs): #각 단어마다
						#그 단어의 window안에 들어가는 것들의 위치 idx를 정한다
            if window <= 0: #window = -1이면
                b, e = 0, n
            else:
                b = max(0, i - window)
                e = min(i + window, n)
		
            for j in range(b, e):	#window안에서
                if i == j: #window내에 같은 단어가 있으면 co-occurence로 치지 않음
                    continue
								#window 내에 다른 단어가 있으면
                counter[(v, vocabs[j])] += 1 #기준점 단어는 이 단어와 연결됨
                counter[(vocabs[j], v)] += 1 #이 단어 입장에서도 기준점 단어와 연결됨
    counter = {k:v for k,v in counter.items() if v >= min_cooccurrence}
    n_vocabs = len(vocab_to_idx)
    return dict_to_mat(counter, n_vocabs, n_vocabs)


from collections import defaultdict

def cooccurrence(tokens, vocab_to_idx, window=2, min_cooccurrence=2):
    counter = defaultdict(int)
    for s, tokens_i in enumerate(tokens):
				#tokens에서 단어장에 있는 단어만 꺼내서 idx만 기록한다. 토큰이 [1,3,10]같은 형태가 된다
        vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
        n = len(vocabs) #vocabs는 문장 하나이다. n = 문장의 길이
        for i, v in enumerate(vocabs): #각 단어마다
						#그 단어의 window안에 들어가는 것들의 위치 idx를 정한다
            if window <= 0: #window = -1이면
                b, e = 0, n
            else:
                b = max(0, i - window)
                e = min(i + window, n)
		
            for j in range(b, e):	#window안에서
                if i == j: #window내에 같은 단어가 있으면 co-occurence로 치지 않음
                    continue
								#window 내에 다른 단어가 있으면
                counter[(v, vocabs[j])] += 1 #기준점 단어는 이 단어와 연결됨
                counter[(vocabs[j], v)] += 1 #이 단어 입장에서도 기준점 단어와 연결됨
    counter = {k:v for k,v in counter.items() if v >= min_cooccurrence}
    n_vocabs = len(vocab_to_idx)
    return dict_to_mat(counter, n_vocabs, n_vocabs)

from scipy.sparse import csr_matrix

def dict_to_mat(d, n_rows, n_cols):
    rows, cols, data = [], [], []
    for (i, j), v in d.items():
        rows.append(i)
        cols.append(j)
        data.append(v)
    return csr_matrix((data, (rows, cols)), shape=(n_rows, n_cols))
	
def word_graph(sents, tokenize = None, min_count=2, window=2, min_cooccurrence=2):
    idx_to_vocab, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)
    tokens = [tokenize(sent) for sent in sents]
    g = cooccurrence(tokens, vocab_to_idx, window, min_cooccurrence)
    return g, idx_to_vocab, vocab_to_idx


import networkx as nx

con = sqlite3.connect("./training.db")


query = """
SELECT *
FROM
    naver_news
"""

df_naver_news = pd.read_sql(query, con)
news = df_naver_news.content

G, id2word, word2id = word_graph(news, tokenize= tokenize, min_count=2, window=2, min_cooccurrence=2)
# idx_KJY = word2id['김정은']
print( word2id )
word_graph_nx = nx.from_scipy_sparse_matrix(G)
p = nx.shortest_path_length(word_graph_nx, source = idx_KJY)
print(p)