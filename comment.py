import selenium
from selenium import webdriver  # selenium 프레임 워크에서 webdriver 가져오기
from bs4 import BeautifulSoup
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

url = 'https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=110&oid=028&aid=0002498556'

browser = webdriver.Chrome('../chromedriver.exe',options=chrome_options) #put this line inside the function def, or chrome winodws keeps opening
rep_url = '{}&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews417%2C0000512678%26sort%3Dlikability'.format(url)    
browser.implicitly_wait(4) #웹 드라이버
browser.get(rep_url)
    #더보기 계속 클릭하기

while True:
    try:
        see_more_button = browser.find_element_by_css_selector('.u_cbox_page_more')
        see_more_button.click()        
        time.sleep(1)
    except:
        break
        #댓글추출
html = browser.page_source
soup = BeautifulSoup(html, 'lxml')

litags = soup.select('div.u_cbox_comment_box > div.u_cbox_area')


for litag in litags:
    litag.select('div.u_cbox_text_wrap > span.u_cbox_contents')[0].text#댓글
    litag.select('div.u_cbox_tool > div.u_cbox_recomm_set > a')[0].select('em.u_cbox_cnt_recomm')[0].text#비추천
    litag.select('div.u_cbox_tool > div.u_cbox_recomm_set > a')[1].select('em.u_cbox_cnt_unrecomm')[0].text#댓글작성날짜
    litag.select('div.u_cbox_info_base > span.u_cbox_date')[0].text#답글수
    litag.select('div.u_cbox_tool > a.u_cbox_btn_reply > span.u_cbox_reply_cnt')[0].text
