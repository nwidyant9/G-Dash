from dash import Dash, html, dcc, callback, Output, Input, State
from dash import dash_table
import pandas as pd
import numpy as np
import dash
import os
import io
import base64
import datetime
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Add logo and images
my_logo = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/Pictures/g-dash-high-resolution-logo-white-on-transparent-background.png'
my_logo_image = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/Pictures/g-dash-high-resolution-logo-color-on-transparent-background.png'

# Load Data
data_mme1_2023 = 'https://raw.githubusercontent.com/nwidyant9/Project00/main/dummy.csv'
mme1_2023 = pd.read_csv(data_mme1_2023)

# Dummy Global variable
global df
global df_preprocessed
global mesin_options
global values
df = pd.DataFrame()  # Initialize an empty DataFrame
df_preprocessed = pd.DataFrame()
mesin_options = None
values = None

# Preprocessing Data MME1
mme1_2023 = mme1_2023.dropna(subset=['Mesin'])
mme1_2023.loc[mme1_2023['Mesin'] == 'DGM 2 (KORAN)', 'Target'] = mme1_2023.loc[mme1_2023['Mesin'] == 'DGM 2 (KORAN)', 'Target'].fillna(0)
mme1_2023[['Load_time', 'Freq', 'Menit']] = mme1_2023[['Load_time', 'Freq', 'Menit']].fillna(0)
mme1_2023['BD_percent'] = round((mme1_2023['Menit'] / mme1_2023['Load_time']) * 100, 2)
mme1_2023['BD_percent'] = mme1_2023['BD_percent'].fillna(0)
mme1_2023.reset_index(drop=True, inplace=True)
modes_by_mesin = mme1_2023.groupby('Mesin')['Target'].transform(lambda x: x.mode().iloc[0])
mme1_2023['Target'] = mme1_2023['Target'].fillna(modes_by_mesin)
mme1_2023['Target_percent'] = round(mme1_2023['Target'] * 100, 2)
mme1_2023['Status'] = np.where(mme1_2023['BD_percent'] <= mme1_2023['Target_percent'], 'OK', 'Not OK')
Total = mme1_2023['Load_time'].sum()

# Preprocessing Data MME2

# Define the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Make option for dropdown
machine_options = [{'label': mesin, 'value': mesin} for mesin in mme1_2023['Mesin'].unique()]

# Define home_layout
home_layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Img(src=my_logo_image, style={'width': '100%', 'height': 'auto', 'margin-top': '100px', 'align': 'center'}),
                width={"size": 6, "offset": 3}
            )
        ),
        dbc.Row(
            dbc.Col(
                html.H1("Welcome to G-DASH", className="mt-3 mb-4"),
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P("Get started by uploading your CSV files and exploring the dashboard."),
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button("Get Started", id='get-started-button', n_clicks=0, color='primary', className='mt-3'),
                width='auto'
            )
        ),
    ]
)

# Define dashboard layout
dashboard_layout = dbc.Container(
    [
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop CSV Files or ',
                html.A('Select CSV Files', style={'color': 'blue'})
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin-top': '100px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        dbc.Button('View File', id='view-button', n_clicks=0, color='primary', style={'margin-top': '20px', 'margin-right': '5px'}),
        dbc.Button('Preprocessing', id='preprocess-button', n_clicks=0, color='primary', style={'margin-top': '20px', 'margin-right': '5px'}),
        dbc.Button('Visualize', id='visualize-button', n_clicks=0, color='primary', style={'margin-top': '20px', 'margin-right': '5px'}),
        html.H3("Uploaded Data"),
        html.Div(id='output-data-upload'),
        html.Div(id='upload-message', style={'margin': '10px'}),
        html.H3("Preprocessed Data"),
        dash_table.DataTable(id='preprocessed-table', columns=[], data=[], page_size=10),
        html.H3("Visualized Data"),
    ]
)

# Display the MME1 layout
mme1_layout = dbc.Container(
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
            ),
        ]),

        dbc.Row([
            dbc.Col(
                dcc.Graph(id='line-plot'),
                width=6,
            ),
            dbc.Col(
                dcc.Graph(id='bar-plot'),
                width=6,
            )
        ], className="mb-5"),

        dbc.Row([
            dbc.Col(
                dcc.Graph(id='pie-chart'),
                width=6,
            ),
        ], className="mb-5"),

        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='bulan-dropdown',
                    options=[{'label': bulan, 'value': bulan} for bulan in mme1_2023['Bulan'].unique()],
                    value=mme1_2023['Bulan'].unique()[0],
                    className='mb-3'
                ),
                width=3
            )
        ]),

        dbc.Row([
            dbc.Col(
                dcc.Graph(id='new-bar-plot'),
                width=6,
            ),
            dbc.Col(
                dcc.Graph(id='percent-bar-plot'),
                width=6,
            ),
        ], className="mb-5")

    ], style={
        'margin-top': '100px',
        'position': 'static',
        },
)

# Display the Linear Regression layout
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

# Define the app layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", active="exact")),
                dbc.NavItem(dbc.NavLink("Linear Regression (BETA)", href="/linreg", active="exact")),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem(dbc.NavLink("MME1", href="/mme1-2023", active="exact", style={'color': 'blue'})),
                    ],
                    label="Examples",
                    nav=True,
                ),
            ],
            brand=html.Img(src=my_logo, height='55px'),
            brand_href="/",
            color="primary",
            dark=True,
            style={'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'z-index': '100'}
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
        return home_layout
    elif pathname == '/dashboard':
        return dashboard_layout
    elif pathname == '/linreg':
        return linreg_layout
    elif pathname == '/mme1-2023':
        return mme1_layout
    
@app.callback(
    Output('url', 'pathname'),
    Input('get-started-button', 'n_clicks')
)
def navigate_to_dashboard(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return '/dashboard'
    return '/'
    
@app.callback(
    Output('line-plot', 'figure'),
    Output('bar-plot', 'figure'),
    Output('pie-chart', 'figure'),
    Input('machine-dropdown', 'value'),
)
def update_graph(value):
    dff = mme1_2023[mme1_2023.Mesin == value]

    line_fig = px.line(dff, x='Bulan', y=['BD_percent', 'Target_percent'], markers=True, title='Perbandingan Persentase Break Down dan Target')
    line_fig.update_layout()

    bar_fig = px.bar(dff, x='Bulan', y='Freq', title='Frequensi Break Down per Bulan')
    bar_fig.add_trace(go.Scatter(x=dff['Bulan'], y=dff['Freq'], mode='lines+markers', name='Freq'))

    line_fig.update_layout(
       yaxis_title='Persentase (%)',
       xaxis_title='Bulan'
    )
    
    line_fig.update_traces(name='Break Down %', selector=dict(name='BD_percent'))
    line_fig.update_traces(name='Target %', selector=dict(name='Target_percent'))

    status_counts = dff['Status'].value_counts()
    status_percentages = (status_counts / status_counts.sum()) * 100
    pie_fig = px.pie(status_percentages,
                     values=status_percentages,
                     names=status_percentages.index,
                     title='Persentase Status Break Down setiap Mesin',
                     labels={'label': 'Status'},
                     hole=.3,
                     color_discrete_sequence=['blue', 'red'],
                     category_orders={'Status': ['OK', 'Not OK']}
                    )

    return line_fig, bar_fig, pie_fig

def update_plots(value):
    line_fig, bar_fig = update_graph(value)
    return line_fig, bar_fig

@app.callback(
    Output('new-bar-plot', 'figure'),
    Output('percent-bar-plot', 'figure'),
    Input('bulan-dropdown', 'value')
)
def new_update_graph(bulan_value):
    dfm = mme1_2023[mme1_2023.Bulan == bulan_value]

    new_bar_fig = px.bar(dfm, x='Mesin', y='Freq', title='Frequensi Break Down per Bulan', color='Mesin', text='Freq')
    new_bar_fig.update_traces(textposition='outside', cliponaxis=False)
    percent_bar_fig = px.bar(dfm, x='Mesin', y='BD_percent', title='Persentase Break Down per Bulan', color='Mesin', text='BD_percent')
    percent_bar_fig.update_traces(textposition='outside', cliponaxis=False)

    new_bar_fig.update_layout(
       yaxis_title='Frekuensi',
       xaxis_title='Mesin'
    )

    percent_bar_fig.update_layout(
       yaxis_title='Persentase (%)',
       xaxis_title='Mesin'
    )

    return new_bar_fig, percent_bar_fig

def new_update_plots(bulan_value):
    new_bar_fig = new_update_graph(bulan_value)
    percent_bar_fig = new_update_graph(bulan_value)
    return new_bar_fig, percent_bar_fig

def parse_contents(contents, filename, date):
    global df   # Declare df as a global variable outside the try block
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'Invalid file format. Please upload a CSV file'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            page_size=10
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@callback([Output('output-data-upload', 'children'),
           Output('upload-message', 'children')],
           [Input('view-button', 'n_clicks')],
           [State('upload-data', 'contents'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified')])
def view_file(n_clicks, list_of_contents, list_of_names, list_of_dates):
    global df   # Declare df as a global variable in the callback
    if n_clicks > 0 and list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        message = "DataFrame upload successfully!"
        return children, message
    else:
        return dash.no_update
    
def preprocess_data():
    global df  # Access the global df variable

    if df.empty:
        return "DataFrame is empty. Upload data first."

    # Perform data preprocessing (scaling 'x' and 'y' columns to [0, 1])
    df = df.dropna(subset=['Mesin'])
    df.loc[df['Mesin'] == 'DGM 2 (KORAN)', 'Target'] = df.loc[df['Mesin'] == 'DGM 2 (KORAN)', 'Target'].fillna(0)
    df[['Load_time', 'Freq', 'Menit']] = df[['Load_time', 'Freq', 'Menit']].fillna(0)
    df['BD_percent'] = round((df['Menit'] / df['Load_time']) * 100, 2)
    df['BD_percent'] = df['BD_percent'].fillna(0)
    df.reset_index(drop=True, inplace=True)
    modes_by_mesin = df.groupby('Mesin')['Target'].transform(lambda x: x.mode().iloc[0])
    df['Target'] = df['Target'].fillna(modes_by_mesin)
    df['Target_percent'] = round(df['Target'] * 100, 2)
    df['Status'] = np.where(df['BD_percent'] <= df['Target_percent'], 'OK', 'Not OK')

    # Assign the preprocessed data to a new global variable df_preprocessed
    global df_preprocessed
    df_preprocessed = df.copy()

    global mesin_options
    mesin_options = [{'label': mesin, 'value': mesin} for mesin in df_preprocessed['Mesin'].unique()]

    global values
    values = df_preprocessed['Mesin'].unique()[0]

    return "Data preprocessed successfully!"

@callback(Output('preprocessed-table', 'columns'),
          Output('preprocessed-table', 'data'),
          Input('preprocess-button', 'n_clicks'))
def preprocess_callback(n_clicks):
    if n_clicks > 0:
        message = preprocess_data()
        if df_preprocessed.empty:
            return [], []
        else:
            columns = [{'name': i, 'id': i} for i in df_preprocessed.columns]
            data = df_preprocessed.to_dict('records')
            return columns, data
    else:
        return [], []

if __name__ == '__main__':
    app.run_server(debug=True)