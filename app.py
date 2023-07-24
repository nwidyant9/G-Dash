from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

my_logo = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/Pictures/gdash.png'

# Load Data
data_mme1_2023 = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/dummy.csv'
mme1_2023 = pd.read_csv(data_mme1_2023)

# Preprocessing Data MME 1
mme1_2023 = mme1_2023.dropna(subset=['Mesin'])
mme1_2023[['Load_time', 'Freq', 'Menit']] = mme1_2023[['Load_time', 'Freq', 'Menit']].fillna(0)
mme1_2023['BD_percent'] = round((mme1_2023['Menit'] / mme1_2023['Load_time']) * 100, 2)
mme1_2023['BD_percent'] = mme1_2023['BD_percent'].fillna(0)
mme1_2023['Target_percent'] = round(mme1_2023['Target'] * 100, 2)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

machine_options = [{'label': mesin, 'value': mesin} for mesin in mme1_2023['Mesin'].unique()]

# Define the layouts
mme1_layout = linreg_layout = dbc.Container(
    [
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
        ], className="mb-5"),
    ],
)

linreg_layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Linear Regression", className="mt-3 mb-4"),
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P("This is the content of the Linear Regression."),
            )
        ),
    ],
    className="mt-4"
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            children=[
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=my_logo, height="30px")),
                        ],
                        align="center",
                    ), href="/"
                ),
                dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                dbc.NavItem(dbc.NavLink("Linear Regression (BETA)", href="/linreg", active="exact")),
                #dbc.NavItem(dbc.NavLink("Another Page", href="/another-page", active="exact")),
                dbc.DropdownMenu(
                    [dbc.DropdownMenuItem(dbc.NavLink("MME1", href="/another-page", active="exact", style={'color': 'blue'})),
                     dbc.DropdownMenuItem(dbc.NavLink("MME2", href="/another-page", active="exact", style={'color': 'blue'})),
                    ],
                    label="Visualisasi",
                    nav=True,
                ),
            ],
            brand="G-DASH",
            brand_href="/",
            color="primary",
            dark=True,
        ),
        html.Div(id='page-content')
    ]
)

@app.callback(
        Output('page-content', 'children'),
          [Input('url', 'pathname')]
)

def display_page(pathname):
    if pathname == '/':
        return html.H1(children='Dashboard', className='mt-3 mb-4')
    elif pathname == '/linreg':
        return linreg_layout
    elif pathname == '/another-page':
        return mme1_layout
    
@app.callback(
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
    app.run_server(debug=True)