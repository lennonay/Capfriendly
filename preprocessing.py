import pandas as pd
import numpy as np

df = pd.read_csv('data/player_season.csv', index_col = 0)
df = df[df['season'].notnull()]
df['season'] = df['season'].astype("int")

main_df = df[df['games'].notnull()].drop('team',axis=1).copy()

onice_cols = [col for col in main_df.columns if 'OnIce' in col]

for col in onice_cols:
    main_df[col]=pd.to_timedelta('00:'+main_df[col]).dt.total_seconds()


main_df.sort_values(['fullName','season'],inplace=True)
main_df = main_df.groupby(['fullName','season','Current_team','Pos']).sum().reset_index()

col_list = list(main_df.columns)
col_list = [col for col in col_list if col not in (['fullName','season','Current_team','Pos'])]
cum_list = []

for col in col_list:
    cum_list.append(col+'_cum')
    main_df[col + '_cum'] = main_df.groupby(['fullName','Current_team','Pos'])[col].cumsum()

main_df['nhl_season'] = main_df.groupby(['fullName']).cumcount() + 1
result_df = main_df[['fullName','Current_team','season','Pos','nhl_season']+cum_list].copy()



result_df.to_csv('data/processed_data.csv',index=False)