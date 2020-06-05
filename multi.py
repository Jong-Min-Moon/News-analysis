import work

from work import Crawler
from multiprocessing import Pool
import schedule
from pprint import pprint
import time
from datetime import datetime


import pickle



if __name__ == '__main__':
        
    def job1(today):
        #today = datetime.today().strftime('%Y-%m-%d')
        #today = '2020-05-29'
        today_crawl = Crawler('육군', today, today, 'D:/crawling')
        today_crawl.mkpath()

        today_crawl.getNClinks(0)
        #today_crawl.getNC(0)
        
        texts = today_crawl.NC_urls[0]
        texts_sent = work.add_sent_score(texts)
        work.Do_LDA(texts_sent, 6, 4000)
    
    
    job1('2020-06-02')
    job1('2020-06-01')
    job1('2020-05-31')
    job1('2020-05-30')
    job1('2020-05-29')
    job1('2020-05-28')
    job1('2020-05-27')
    job1('2020-05-26')
    job1('2020-05-25')


    # schedule.every().day.at("23:50:00").do(job1)

    # from pprint import pprint

    # print("Job 확인")
    # pprint(schedule.jobs)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    
    

    

               
