import work
import pandas as pd

tot = pd.read_csv('D:/total.csv')
tot = tot.loc[:, ['press', 'title', 'url', 'content', 'time']]

first = work.add_sent_score( tot.iloc[:1000, :].copy() )

for i in range(1000, len(tot.index), 1000):
    temp_table = tot.iloc[i:i+1000, :].copy()
    #print(temp_table.iloc[1,:])
    first = first.append( work.add_sent_score(temp_table), ignore_index=True )
    print(i,'th run')

first.to_csv('D:/total_sent.csv')
