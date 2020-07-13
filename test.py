import LDA
import pandas as pd

news = pd.read_csv('NN_2020.05.31.csv')

lda_model, corpus = LDA.Do_LDA(news, 5)

#print(LDA.format_topics_sentences(lda_model, corpus, news.title))
print(LDA.most_relev_doc(lda_model, corpus, news.title))
