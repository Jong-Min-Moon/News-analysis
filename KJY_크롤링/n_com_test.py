import pandas as pd
import combined_training as ct
import crawl

ct.do_crawl('공군 황제', '2020.06.12', initialize = True)
# crawl_daterange_BSY = pd.date_range('2020.07.06', '2020.07.25')
# for crawl_date_obj in crawl_daterange_BSY:
#     ct.do_crawl('백선엽', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)
