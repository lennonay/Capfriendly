import requests
import pandas as pd
import json
import datetime

def get_roster(link):
    response = requests.get(master_url + link + '?expand=team.roster')
    team_data = response.json()

    roster_df = pd.DataFrame(team_data['teams'][0]['roster']['roster'])

    roster_df = pd.concat([roster_df.drop(['person'], axis =1), roster_df['person'].apply(pd.Series)], axis =1)
    roster_df = pd.concat([roster_df.drop(['position'], axis =1), roster_df['position'].apply(pd.Series)], axis =1)

    roster_df = roster_df[roster_df['abbreviation']!='G']
    roster_df.drop(['jerseyNumber','id','code','name','type'],axis=1, inplace=True)
    roster_df.rename(columns = {'abbreviation':'Pos'}, inplace=True)
    roster_records = roster_df.to_dict('records')

    return roster_records

def get_player_stats(link):
    response = requests.get(master_url + link + '/stats?stats=yearByYear')
    player_data = response.json()
    player_df = pd.DataFrame(player_data['stats'][0]['splits'])

    nhl_stat = pd.concat([player_df.drop(['league'],axis=1), player_df['league'].apply(pd.Series)], axis =1)
    nhl_index = nhl_stat.index[nhl_stat['name']=='National Hockey League'].tolist()

    player_df = player_df.drop(['league'],axis=1).loc[nhl_index]

    player_df = pd.concat([player_df.drop(['stat'],axis=1), player_df['stat'].apply(pd.Series)], axis =1)
    player_df = pd.concat([player_df.drop(['team'],axis=1), player_df['team'].apply(pd.Series)], axis =1)

    player_df.drop(['sequenceNumber','id','link'], axis=1, inplace=True, errors='ignore')
    player_df.sort_values('season',ascending=False,inplace=True)
    player_df.reset_index(drop=True, inplace=True)
    player_df.rename(columns = {'name':'team'}, inplace=True)
    player_records = player_df.to_dict('records')

    return player_records

def expand_row(df, func, col, drop_col, before):
    df['temp'] = df[col].apply(func)
    if before ==True:
        result_df = df.explode('temp', ignore_index=True).drop(drop_col,axis=1)
        result_df = pd.concat([result_df.drop(['temp',], axis=1), 
                                result_df['temp'].apply(pd.Series)], axis=1)
    elif before ==False:
        result_df = df.explode('temp', ignore_index=True)
        result_df = pd.concat([result_df.drop(['temp',], axis=1), 
                                result_df['temp'].apply(pd.Series)], axis=1).drop(drop_col,axis=1)
    return result_df

print(datetime.datetime.now())

master_url = "https://statsapi.web.nhl.com"

response = requests.get(master_url + "/api/v1/teams")
data = response.json()
team_df = pd.DataFrame(data['teams'])[['name','link']]
team_df.rename(columns = {'name':'Current_team'},inplace=True)

roster_df = expand_row(team_df, get_roster, 'link','link', True)
season_stats_df = expand_row(roster_df, get_player_stats, 'link',[0,'link'], False)

season_stats_df.to_csv('data/player_season.csv')

print(datetime.datetime.now())