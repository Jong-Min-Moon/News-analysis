
import NLP
import crawl
import schedule
from pprint import pprint
import time
from datetime import datetime


import pickle

import sqlite3



if __name__ == '__main__':
    con = sqlite3.connect("./rokanews.db")
    #with open('schema.sql') as fp:
    #    con.executescript(fp.read())
    #con.commit()
    def job1():
        today = datetime.today().strftime('%Y-%m-%d')
        today = '2020-07-17'
        today_crawl = Crawler('육군', today, today, 'D:/crawling')
        

        #뉴스기사
        today_crawl.getNClinks(0)
        texts = today_crawl.NC_urls[0]
        texts_sent = NLP.add_sent_score(texts)

        texts_sent.to_sql('naver_news', con, if_exists = 'append', index = False)
        # lda, corpus = NLP.Do_LDA(texts_sent)
        # LDA_today = NLP.format_topics_sentences(lda, corpus, texts)
        # LDA_today.to_sql('LDA', con, if_exists = 'append', index = False)
        
       # 댓글
        today_crawl.getNC(0)
        NC_table = NLP.add_sent_score(today_crawl.NC)
        NC_table.to_sql('naver_comment', con, if_exists = 'append', index = False)

        # #doc id를 join해서 붙임
        query = 'UPDATE naver_comment SET doc_id = (SELECT doc_id FROM naver_news WHERE url = naver_comment.url) WHERE doc_id IS NULL'  
        cs = con.execute(query)
        print(f'{cs.rowcount} rows are updated.')
        con.commit()
        con.close()

    def job2():
        today = datetime.today().strftime('%Y.%m.%d')
        today = '2020.07.17'
        df = crawl.daily_crawl_naver_news(today)

        df.to_sql('pagerank', con, if_exists = 'append', index = False)
        con.commit()
        con.close()
    # schedule.every().day.at("23:50:00").do(job1)
    job2()
    
    # from pprint import pprint

    # print("Job 확인")
    # pprint(schedule.jobs)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    
    

    

               
