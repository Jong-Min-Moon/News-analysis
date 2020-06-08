import pickle
def add_word(word):
    with open('korean_stopwords.txt', 'rb') as f:
        stopwords = pickle.load(f)
    if word not in stopwords:
        stopwords.append(word)
        print('added ' + word)
    else:
        print('이미 있음')

    with open('korean_stopwords.txt', 'wb') as f:
        pickle.dump(stopwords, f)
    
    

add_word('그')



# with open('korean_stopwords.txt', 'rb') as f:
#     stopwords = pickle.load(f)

# with open('korean_stopwords.txt', 'wb') as f:
#         pickle.dump(stop_list, f)