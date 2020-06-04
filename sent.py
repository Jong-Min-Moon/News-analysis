
import work
from work import add_sent_score
import pandas as pd
import numpy as np



def search_by_score(data, size  = 20, asc = True):
    temp_table = data[ data.label == 'NA' ].sort_values(by = 'sent_score', ascending = asc)[:size]
    print(temp_table)
    for i in range(size):
        og_idx = temp_table.index[i]
        order1 = input('n: 다음 기사 출력')
        while order1 != 'n':
            input('n을 눌러 다음 기사 출력')
        if order1 == 'n':
            print('{}번째 기사 제목: {}'.format(og_idx, temp_table.iloc[i, 1]))
            print('기사 내용', temp_table.iloc[i, 3])

        order2 = input('1, 0, -1, s, d 중 하나 입력')    
        while order2 not in ['1', '0', '-1', 's', 'd']:
            order2 = input('1, 0, -1, s, d 중 하나 입력')   
        for user_input in ['1', '0', '-1', 's', 'd']:
            if order2 == user_input:
                print( '{}번째 기사를 {}로 분류함'.format(temp_table.index[i], order2))
                data.loc[og_idx, 'label'] = user_input
    print('완료')
    data.to_csv('D:/crawling/crawl_육군_2005-05-10_2020-05-18/NC/temp/naver_comment_url육군_2005.05.10.csv', index = False)


news = pd.read_csv( 'D:/crawling/crawl_육군_2005-05-10_2020-05-18/NC/temp/naver_comment_url육군_2005.05.10.csv' )
news_scr = add_sent_score(news)

size_input = int(input('기사 수'))
P_or_N = bool(input('부정적인 기사? True or False'))

search_by_score(news_scr, size  = size_input, asc = P_or_N)