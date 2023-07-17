from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Load Data
data_mme1_2023 = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/dummy.csv'
mme1_2023 = pd.read_csv(data_mme1_2023)

# Preprocessing Data
mme1_2023 = mme1_2023.dropna(subset=['Mesin'])
mme1_2023[['Load_time', 'Freq', 'Menit']] = mme1_2023[['Load_time', 'Freq', 'Menit']].fillna(0)
mme1_2023['BD_percent'] = round((mme1_2023['Menit'] / mme1_2023['Load_time']) * 100, 2)
mme1_2023['BD_percent'] = mme1_2023['BD_percent'].fillna(0)
mme1_2023['Target_percent'] = round(mme1_2023['Target'] * 100, 2)

# Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

machine_options = [{'label': mesin, 'value': mesin} for mesin in mme1_2023['Mesin'].unique()]

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Linear Regression (BETA)", href="#")),
                dbc.NavItem(dbc.NavLink("Link 2", href="#")),
            ],
            brand="Dashboard",
            brand_href="#",
            color="primary",
            dark=True,
        ),

        html.H1(children='Dashboard MME 1 2023', className='mt-3 mb-4'),

        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='machine-dropdown',
                    options=machine_options,
                    value=mme1_2023['Mesin'].unique()[0],
                    className='mb-3'
                ),
                width=3
            )
        ]),

        dbc.Row([
            dbc.Col(
                dcc.Graph(id='line-plot'),
                width=6
            ),
            dbc.Col(
                dcc.Graph(id='bar-plot'),
                width=6
            )
        ], className='mb-5'),
    ]
)

@callback(
    Output('line-plot', 'figure'),
    Output('bar-plot', 'figure'),
    Input('machine-dropdown', 'value')
)

def update_graph(value):
    dff = mme1_2023[mme1_2023.Mesin == value]

    line_fig = px.line(dff, x='Bulan', y=['BD_percent', 'Target_percent'], markers=True, title='Perbandingan Persentase Break Down dan Target')
    line_fig.update_layout(height=300)

    bar_fig = px.bar(dff, x='Bulan', y='Freq', title='Frequensi Break Down per Bulan')
    bar_fig.add_trace(go.Scatter(x=dff['Bulan'], y=dff['Freq'], mode='lines+markers', name='Freq'))

    line_fig.update_layout(
       yaxis_title='Persentase (%)',
       xaxis_title='Bulan'
    )
    
    line_fig.update_traces(name='Break Down %', selector=dict(name='BD_percent'))
    line_fig.update_traces(name='Target %', selector=dict(name='Target_percent'))

    return line_fig, bar_fig

def update_plots(value):
    line_fig, bar_fig = update_graph(value)
    return line_fig, bar_fig

if __name__ == '__main__':
    app.run(debug=True)