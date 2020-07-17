import LDA
import sqlite3
import pandas as pd

con = sqlite3.connect('./rokanews.db')
docs = pd.read_sql('SELECT * FROM NN WHERE time = "2020.06.22"', con)

lda, corpus = LDA.Do_LDA(docs)

print( LDA.format_topics_sentences(lda, corpus, docs) )
print( LDA.most_relev_doc(lda, corpus, docs)) 

