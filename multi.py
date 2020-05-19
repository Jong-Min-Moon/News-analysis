import work
from work import Crawler
from multiprocess import Pool
import schedule
from pprint import pprint
import time
from datetime import datetime




if __name__ == '__main__':


    def job1():
        today = datetime.today().strftime('%Y-%m-%d')
        #today = '2020-03-02'
        today_crawl = Crawler('육군', today, today, 'D:/crawling')
        today_crawl.mkpath()
    
        with Pool(2) as pool:
            pool.map(today_crawl.getNClinks, range(len(today_crawl.d_range)))
        
    job1()  
    #schedule.every().day.at("23:58:30").do(job1)

    #from pprint import pprint

    #print("Job 확인")
    #pprint(schedule.jobs)

    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)

    
    

    

               