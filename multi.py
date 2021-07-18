import work

from work import Crawler
from multiprocessing import Pool
import schedule
from pprint import pprint
import time
from datetime import datetime


import pickle
import sqlite3


if __name__ == '__main__':
    con = sqlite3.connect("./crawlTest/rokanews.db")

    #rokanews.db 파일 리셋
    with open('schema.sql') as fp:
        con.executescript(fp.read())
    con.commit()

    def job1():
        today = datetime.today().strftime('%Y-%m-%d')
        today_crawl = Crawler('육군', today, today, './crawlTest')


        #뉴스기사
        today_crawl.getNClinks(0)
        # texts = today_crawl.NC_urls[0]
        # texts_sent = work.add_sent_score(texts)
        # LDA_today, NN_table = work.Do_LDA(texts_sent, 6, 4000)

        # NN_table.to_sql('NN', con, if_exists = 'append', index = False)
        # LDA_today.astype(str).to_sql('LDA', con, if_exists = 'append', index = False)
        
        # #댓글
        # today_crawl.getNC(0)
        # NC_table = work.add_sent_score(today_crawl.NC)
        # NC_table.to_sql('NC', con, if_exists = 'append', index = False)

        # #doc id를 join해서 붙임
        # query = 'UPDATE NC SET doc_id = (SELECT doc_id FROM NN WHERE url = NC.url) WHERE doc_id IS NULL'  
        # cs = con.execute(query)
        # print(f'{cs.rowcount} rows are updated.')
        # con.commit()


    # schedule.every().day.at("23:50:00").do(job1)
    job1()
    
    # from pprint import pprint

    # print("Job 확인")
    # pprint(schedule.jobs)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    
    

    

               
