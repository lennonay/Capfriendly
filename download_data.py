import pandas as pd

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

master_df.to_csv('data/cap_data_1723.csv', index=False)