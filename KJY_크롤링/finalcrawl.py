import pandas as pd
import combined_training as ct

#김정은 사망은 4월 22일부터
ct.do_crawl('김정은', '2020.04.13', initialize = True)
crawl_daterange_BSY = pd.date_range('2020.04.14', '2020.05.10')
for crawl_date_obj in crawl_daterange_BSY:
    ct.do_crawl('김정은', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)


#김정은 위독은 4월 21일부터
# crawl_daterange_BSY = pd.date_range('2020.04.15', '2020.05.10')
# for crawl_date_obj in crawl_daterange_BSY:
#     ct.do_crawl('김정은 위독', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)


# crawl_daterange_BSY = pd.date_range('2020.04.15', '2020.05.10')
# for crawl_date_obj in crawl_daterange_BSY:
#     ct.do_crawl('김정은 중병', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)

# crawl_daterange_BSY = pd.date_range('2020.04.15', '2020.05.10')
# for crawl_date_obj in crawl_daterange_BSY:
#     ct.do_crawl('김정은 유고', crawl_date_obj.strftime('%Y.%m.%d'), initialize = False)