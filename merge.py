import pandas as pd
import os
pat = 'D:/crawling/crawl_육군_2005-05-10_2020-05-18/NC/temp/url'
file_list = os.listdir(pat)
file_list.sort()

first = pd.read_csv( pat + '/' + file_list[0] )

for filename in file_list[1:]:
    first = first.append(pd.read_csv(pat + '/' + filename), ignore_index=True)
    print(filename)

first = pd.read_csv('D:/total.csv').append(first, ignore_index = True)
first.to_csv('D:/total.csv')




first = pd.read_csv('D:/total.csv')

first.time.value_counts()