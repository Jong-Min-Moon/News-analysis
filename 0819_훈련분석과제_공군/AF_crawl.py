import pandas as pd
import combined_training as ct

ct.do_crawl('공군 황제', '2020.06.12', initialize = True)
crawl_daterange_BSY = pd.date_range('2020.06.13', '2020.08.12')
for crawl_date_obj in crawl_daterange_BSY:
    ct.do_crawl('공군 황제', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)

crawl_daterange_BSY = pd.date_range('2020.06.12', '2020.08.12')
for crawl_date_obj in crawl_daterange_BSY:
    ct.do_crawl('공군 특혜', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)