import pandas as pd
import combined_training as ct


crawl_daterange_BSY = pd.date_range('2020.07.13', '2020.08.14')
for crawl_date_obj in crawl_daterange_BSY:
    ct.do_crawl('백선엽', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)
# ct.do_crawl('백선엽', '2020.08.15', initialize = False)