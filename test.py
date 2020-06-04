import work
from work import Crawler



today_crawl = Crawler('군사과학', '2020-05-24', '2020-05-25', 'D:/crawling')
today_crawl.mkpath()


today_crawl.getNClinks(0)

today_crawl.getNC(0)
    