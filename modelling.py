import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import pickle
import plotly.express as px

df = pd.read_csv('data/processed_data.csv')
df = df[df['Pos']!='D']

features = [col for col in df.columns if col not in (['fullName','season','Current_team','Pos'])]
X = df[features]

num_neighbors = 5
nn_model = NearestNeighbors(n_neighbors=num_neighbors)
nn_model.fit(X)

query = df[df['fullName'] == 'Elias Pettersson'].iloc[[-1]].drop(['fullName','season','Current_team','Pos'], axis=1)
distances, indices = nn_model.kneighbors(query)

nearest_neighbors = df.iloc[indices[0]]

pickle.dump(nn_model, open('cluster_f.pkl', 'wb'))

petey_df = df[df['fullName'] == 'Elias Pettersson']

fig = px.line(petey_df, x = 'nhl_season', y = 'points_cum')
fig.update_layout(
    xaxis=dict(tickvals=petey_df['nhl_season'],ticktext=petey_df['nhl_season'])
)

nearest_neighbors.iloc[1]['fullName']
