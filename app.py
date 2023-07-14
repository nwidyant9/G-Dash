from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# Load Data
data_path = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/dummy.csv'
df = pd.read_csv(data_path)

# Preprocessing Data
df = df.dropna(subset=['Mesin'])
df[['Load_time', 'Freq', 'Menit']] = df[['Load_time', 'Freq', 'Menit']].fillna(0)
df['BD_percent'] = round((df['Menit'] / df['Load_time']) * 100, 2)
df['BD_percent'] = df['BD_percent'].fillna(0)
df['Target_percent'] = round(df['Target'] * 100, 2)

# Dash App
app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='MME 1', style={'textAlign':'center'}),
    dcc.Dropdown(df.Mesin.unique(), '', id='dropdown-selection'),
    dcc.Graph(id='graph-content'),
    dcc.Graph(id='bar-plot')
])

@callback(
    Output('graph-content', 'figure'),
    Output('bar-plot', 'figure'),
    Input('dropdown-selection', 'value')
)

def update_graph(value):
  dff = df[df.Mesin==value]
  fig = px.line(dff, x='Bulan', y=['BD_percent', 'Target_percent'], markers=True, title='Perbandingan Persentase Break Down dan Target')
  bar = px.bar(dff, x='Bulan', y='Freq')
  bar.add_trace(go.Scatter(x=dff['Bulan'], y=dff['Freq'], mode='lines+markers', name='Freq'))

  fig.update_layout(
    yaxis_title='Persentase (%)',
    xaxis_title='Bulan'
  )

  fig.update_traces(name='Break Down %', selector=dict(name='BD_percent'))
  fig.update_traces(name='Target %', selector=dict(name='Target_percent'))

  return fig, bar

def update_plots(value):
    fig, bar = update_graph(value)
    return fig, bar

if __name__ == '__main__':
    app.run(debug=True)