import numpy as np
import pandas as pd
import re, spacy, gensim

# Sklearn
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from pprint import pprint


from gensim.matutils import Sparse2Corpus
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel
from gensim.corpora.dictionary import Dictionary



import pickle
from kiwipiepy import Kiwi
# tokenize 함수를 정의합니다. 한국어 문장을 입력하면 형태소 단위로 분리하고, 
# 불용어 및 특수 문자 등을 제거한 뒤, list로 반환합니다.

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
            if not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S') and word not in stopwords] # 조사, 어미, 특수기호는 제거



def doc2corpus(texts):
    texts_for_CVT = [' '.join(tokenize(sentence)) for sentence in texts]

    vectorizer = CountVectorizer(analyzer='word',       
                             min_df = 6,                        # minimum reqd occurences of a word 
                             max_df = 0.2,
                             stop_words=stopwords,             # remove stop words
                             token_pattern = '[가-힣]{2,}',  # num chars > 3
                            )

    data_vectorized = vectorizer.fit_transform(texts_for_CVT)

    #gensim용 id2word    
    corpus = gensim.matutils.Sparse2Corpus(data_vectorized, documents_columns=False)
    dictionary = Dictionary.from_corpus(corpus,
        id2word = dict((id, word) for word, id in vectorizer.vocabulary_.items()))
    
    return corpus, dictionary


def Do_LDA(df):
    texts = df.content #pd seies
    

    #1. manual cleansing with regexp
    
    #2. tokenize & lemmatize




    #gensim용 corpus. list of (id, occurence) tuples.
    corpus, dic = doc2corpus(texts)
    n_folds = 3
    fold_size = round(len(df)/ n_folds)
    PPL_list = []
    for n_topic in range(1,10 + 1):
        lda_best = LdaModel(corpus = corpus, num_topics = n_topic, id2word = dic)
        fold_divide = np.random.permutation(len(df))
        PPL = 0
        for i in range(n_folds):
            train_idx = np.concatenate( (fold_divide[ : i * fold_size], fold_divide[(i+1) * fold_size : ]) )
            valid_idx = fold_divide[ i * fold_size  : (i+1) * fold_size]

            print('train_idx:', train_idx)
            print('valid_idx:', valid_idx)

            doc_train = texts[train_idx]
            doc_valid = texts[valid_idx]
            print(type(doc_valid))
            corpus, voc = doc2corpus(doc_train)
            lda = LdaModel(corpus = corpus, num_topics = n_topic, id2word = voc)

          

            valid_corpus = []
            for i in range(len(doc_valid)):
                new_doc = doc_valid.iloc[i]
                new_doc_tokened = tokenize(new_doc)
                print(new_doc_tokened)
                new_doc_by_traincorpus = voc.doc2bow( new_doc_tokened )
                print(new_doc_by_traincorpus)
                valid_corpus.append(new_doc_by_traincorpus)

            PPL_now = lda.log_perplexity(valid_corpus)
            print('perplexity:', PPL_now)
            PPL += PPL_now
        PPL_list.append(PPL)
    print('\nPerplexity: ', list(zip( range(1,10+1), PPL_list) ))
    n_topic_best = np.array(PPL_list).argmin() + 1
    print('\n best n_topic:', n_topic_best)


    corpus, voc= doc2corpus(texts)
    lda_best = LdaModel(corpus = corpus, num_topics = n_topic_best, id2word = voc)

    return lda_best, corpus



 #학습한 doc-top 행렬과 top-term 행렬을 이용, dominant topic과 top10 keyword 제시
def format_topics_sentences(ldamodel, corpus, docs):
    sent_topics_df = pd.DataFrame() # 빈 데이터프레임 생성

    # Get main topic in each document
    thetas = ldamodel[corpus] # lda[corpus[i]] : i번째 문헌의 주제 분포 벡터. 즉 theta_i. gensim에서의 형식은 list of tuples.
    for i, theta in enumerate(thetas):      
        theta_sorted = sorted(theta, key = lambda x: (x[1]), reverse=True) #sequence의 list를 n번째 원소 기준으로 정렬하는 방법
        for j, (topic_num, prop_topic) in enumerate(theta_sorted): # Get the Dominant topic, Perc Contribution and Keywords for each document
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Add original text to the end of the output
    contents = pd.Series(docs.title)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    sent_topics_df['time'] = docs.time[0]
    return(sent_topics_df)



#'The most representative sentence for each topic'
#학습한 doc-topic 행렬을 이용, 각 topic별로 그 topic에 대한 확률이 가장 높은 doc을 찾아서 보여주기

def most_relev_doc(ldamodel, corpus, texts):
    df_topic_sents_keywords = format_topics_sentences(ldamodel, corpus, texts)
    
    sent_topics_sorteddf_mallet = pd.DataFrame() #빈 데이터프레임 만들기
    sent_topics_outdf_grpd = df_topic_sents_keywords.groupby('Dominant_Topic') #pd generic groupby. 뒤에 .mean() 등을 붙이면 일반적인 groupby가 됨.

    for i, grp in sent_topics_outdf_grpd: #i는 dominant topic. grp는 해당 토픽에 해당하는 모든 row.
        top1 = grp.sort_values(['Perc_Contribution'], ascending=False).head(1) #오름차순 정렬해서 가장 높은 것 하나 선택(head(1))
        top1['items'] = len(grp)
        sent_topics_sorteddf_mallet = pd.concat([sent_topics_sorteddf_mallet, top1 ], #concat을 쓰는 이유는 .head(1) 자체가 하나의 dataframe이기 때문   
                                                    axis=0) #밑에다 한 row씩 붙이기

    
    sent_topics_sorteddf_mallet.reset_index(drop=True, inplace=True)  # Reset Index   
    sent_topics_sorteddf_mallet.columns = ['Topic_Num', "Topic_Perc_Contrib", "Keywords", "Representative Text", 'time', 'items'] # Format

    return sent_topics_sorteddf_mallet.sort_values(by = 'items', ascending = False)
