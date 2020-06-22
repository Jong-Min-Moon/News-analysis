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
    con = sqlite3.connect("./rokanews.db")

    def job1(today):
        #today = datetime.today().strftime('%Y-%m-%d')
        #today = '2020-05-29'
        today_crawl = Crawler('육군', today, today, 'D:/crawling')
        

        #뉴스기사
        today_crawl.getNClinks(0)
        texts = today_crawl.NC_urls[0]
        texts_sent = work.add_sent_score(texts)
        LDA_today, NN_table = work.Do_LDA(texts_sent, 6, 4000)

        #NN_table.to_sql('NN', con, if_exists = 'append', index = False)
        LDA_today.to_sql('LDA', con, if_exists = 'append', index = False)
        #댓글
        #today_crawl.getNC(0)
        #today_crawl.NC.to_sql('NC', con, if_exists = 'append', index = False)

        #doc id를 join해서 붙임
        #query = 'UPDATE NC SET doc_id = (SELECT doc_id FROM NN WHERE url = NC.url) WHERE doc_id IS NULL'  
        #cs = con.execute(query)
        #print(f'{cs.rowcount} rows are updated.')
        #con.commit()

    # schedule.every().day.at("23:50:00").do(job1)
    job1('2020-06-20')
    # from pprint import pprint

    # print("Job 확인")
    # pprint(schedule.jobs)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    
    

    

               
