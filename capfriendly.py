import pandas as pd
import numpy as np

master_df = pd.DataFrame()

for year in range(2017,2024):
    df = pd.DataFrame()
    page_num = 1
    while True:
        url = 'https://www.capfriendly.com/browse/active/'+ str(year) +'?stats-season=' + str(year) + '&pg=' + str(page_num)
        temp_df = pd.read_html(url, match='PLAYER')[0]
        if temp_df.empty:
            break
        page_num+=1
        df = pd.concat([df,temp_df])
    df['Year'] = year
    master_df = pd.concat([master_df,df])

pattern = r'((\d+)\.)'
master_df['PLAYER'] = master_df['PLAYER'].str.replace(pattern,'', regex=True).str[1:]

df = master_df.copy()

df.replace('-',0, inplace=True)
df.replace(np.nan,0, inplace=True)
df = df.apply(pd.to_numeric, errors = 'ignore')
df.sort_values('Year',inplace=True)

df['TOI'] = np.where(df['TOI'] == 0, '00:00', df['TOI'])
df['TOI'] = pd.to_timedelta('00:'+df['TOI'])

print(df.info())
df['TTOI'] = pd.to_timedelta(df['GP'] * df['TOI']).dt.total_seconds()

list = ['GP','G','A','P','+/-','Sh','TTOI']
cum_list = []

for col in list:
    cum_list.append(col+'_cum')
    df[col + '_cum'] = df.groupby(['PLAYER'])[col].cumsum()

cum_list.insert(0,'PLAYER')
cum_list.extend(('Year','POS'))

result_df = df[df['POS']!='G'][cum_list]
result_df.to_csv('data/cap_data_1723.csv', index=False)