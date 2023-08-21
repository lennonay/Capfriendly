import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
from PIL import Image
import pickle
import requests

df = pd.read_csv('data/processed_data.csv')
df = df[df['Pos']!='D']
contract_df = pd.read_csv('data/cap_data_1723.csv')
columns = ['fullName','nhl_season', 'goals_cum','assists_cum','points_cum']

nn_model = pickle.load(open('cluster_f.pkl', 'rb'))
nhl_logo = Image.open('nhl.png')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
    dbc.Col([html.Img(src=nhl_logo, style ={'width': '100px','display': 'inline-block',}),
             html.H1(' NHL Player Career Trajectory Comparison', style={'display': 'inline-block','text-align': 'center','font-size': '48px',"margin-left": "10px"}),
    ],style={
                    'backgroundColor': 'black',
                    'padding': 20,
                    'color': 'white',
                    'margin-top': 20,
                    'margin-bottom': 20,
                    'text-align': 'center',
                    'border-radius': 3}),
    dbc.Row([
        dbc.Col([
            html.Div([
                'Select Player',
                dcc.Dropdown(id = 'player', value = 'Elias Pettersson',
                             options=[{'label': i, 'value': i} for i in df['fullName'].unique()])]),
            html.Br(),
            html.Div([
                'Select Season',
                dcc.Dropdown(id = 'season')
            ])
        ],md=3,style={
                'background-color': '#e6e6e6',
                'padding': 15,
                'border-radius': 3}),
        dbc.Col([            
            dbc.Col([html.Img(id = 'current_team', style={'width':'100px'}),
            html.Div(id = 'title',style={'display': 'inline-block','text-align': 'center','font-size': '24px'})],
            style={
                    'text-align': 'center',}),
            dcc.Graph(id = 'target_plot'),
            html.Br(),
            html.Div(id = 'closest_player'),
            html.Br(),
            dcc.Store(id= 'close_player_list'),
            dcc.Store(id = 'close_season_list'),
            dash_table.DataTable(
                id = 'contract_table',
                columns=[{'name': i, 'id': i} for i in ['name','season','contract']]
            ),
            html.Br(),
            dash_table.DataTable(
                id = 'table',
                columns=[{'name': i, 'id': i} for i in columns],
                sort_action="native",
                filter_action="native",
            )

        ])
    ])
])

@app.callback(
    Output('season','options'),
    [Input('player','value')]
)
def set_season_options(select_player):
    temp_df = df[df['fullName']==select_player]
    return [{'label': season, 'value': season} for season in temp_df['season']]

@app.callback(
    Output('season', 'value'),
    [Input('season', 'options')])
def set_season_value(available_options):
    return available_options[-1]['value']

@app.callback(
        [Output('current_team','src'), Output('title','children')],
        Input('player','value')
)
def current_team(player):
    team_abrv = pd.read_csv('team_names.csv')
    current_team = df[df['fullName']==player]['Current_team'].max()

    abrv = team_abrv[team_abrv['Team'] == current_team]['Abrv_espn'].max()
    link = 'logos/' + str(abrv) + '.png'
    string = f' Career Trajectory of {player}'
    return Image.open(link), string

@app.callback(
    [Output('closest_player','children'), Output('close_player_list','data'), Output('close_season_list','data')],
    Input('player','value'),
    Input('season','value')
)
def player_nearest(player,season):
    query = df[(df['fullName'] == player) & (season == df['season'])].drop(['fullName','season','Current_team','Pos'], axis=1)
    distances, indices = nn_model.kneighbors(query)
    nearest_neighbors = df.iloc[indices[0]]
    player_lst = []
    season_lst = []
    for i in range(1,4):
        player_lst.append(nearest_neighbors.iloc[i]['fullName'])
        season_lst.append(nearest_neighbors.iloc[i]['season'])
    player_lst = list(player_lst)
    player_lst.insert(0,player)
    player_lst = list(dict.fromkeys(player_lst))
    season_lst.insert(0,season)
    return f'The closest comparison to {player} for season {season} are: ' + str(player_lst[1:])[1:-1].replace('\'',''), player_lst, season_lst

@app.callback(
    [Output('contract_table','data'), Output('contract_table','columns')],
    Input('close_player_list','data'),
    Input('close_season_list','data')
)
def contract_table(player_list,season_list):

    contract_list = []
    age_list = []
    for player, season in zip(player_list, season_list):
        query = contract_df[(contract_df['PLAYER'] == player) & (contract_df['Year'] == int(str(season)[:4])+1)]
        contract_list.append(query['CAP HIT'].max())
        age_list.append(query['AGE'].max())
    
    contract_p_df = pd.DataFrame(zip(player_list, season_list,contract_list, age_list), columns = ['name','season','contract','age'])
    return contract_p_df.to_dict('records'), [{'name': i, 'id': i} for i in contract_p_df.columns]

@app.callback(
    Output('target_plot', 'figure'),[Output('table','data'), Output('table','columns')],
    Input('player', 'value'),
    Input('season','value'),
    Input('close_player_list','data')
)
def taget_df_plot(player, season, player_list):
    color_list = ['red','orange','green','blue']

    season_count = df[(df['fullName'] == player)& (season == df['season'] )]['nhl_season'].max()
    player_df = df[(df['fullName'].isin(player_list)) & (df['nhl_season']<=season_count)].copy()
    player_df['fullName'] = player_df['fullName'].astype("category").cat.set_categories(player_list)

    player_df.sort_values(['fullName','nhl_season'], inplace=True)
    
    color_discrete_map = {player_list[i]: color_list[i] for i in range(len(player_list))}

    fig = px.line(player_df, x = 'nhl_season', y = 'points_cum', color = 'fullName', template = 'seaborn', markers=True,
    color_discrete_map = color_discrete_map)
    fig.update_layout(
        xaxis=dict(tickvals=player_df['nhl_season'],ticktext=player_df['nhl_season'])
    )
    fig.update_traces(patch={"line": {"width": 1}}, opacity = .6)
    fig.update_traces(patch={"line": {"width": 3}}, selector={"legendgroup": player}, opacity = 1)
    return fig,player_df.to_dict('records'), [{'name': i, 'id': i} for i in columns]

if __name__ == '__main__':
    app.run_server(debug=True)