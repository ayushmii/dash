import os
import requests
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flask import Flask
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

styles_path = 'styles.css'  # If the file is in the same directory as your Python script
# styles_path = 'path/to/styles.css'  # If the file is in a different directory

# Check if the file exists
if os.path.isfile(styles_path):
    print(f"The file '{styles_path}' exists.")
    # You can perform additional operations here, such as reading the file contents
    with open(styles_path, 'r') as file:
        print("Openend")
else:
    print(f"The file '{styles_path}' does not exist.")

# Flask app and Dash app
app = Flask(__name__)
dash_app = Dash(server=app, routes_pathname_prefix='/dash/', external_stylesheets=[styles_path, dbc.themes.BOOTSTRAP])

# Default date range
start_date = datetime(2010, 1, 1)
end_date = datetime(2019, 12, 31)

# Fetch department names
dept_names = requests.get(f"http://localhost:5555/departments").json()

# Dash layout
dash_app.layout = dbc.Container([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="assets/logo.png", className="logo"),
                    html.H1("Sanjay Gandhi Postgraduate Institute of Medical Sciences", className="header-title")
                ], className="header-container")
            ], width=12)
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Search Disease Data'),
                    dcc.Input(id='disease-name-input', type='text', placeholder='Enter disease name', className='form-control',
    style={
        'backgroundColor': '#2c2c2c',
        'color': '#ffffff',
        'borderColor': '#4d4d4d'
    }),
                    html.Button('Search', id='search-button', n_clicks=0, className='searchbutton btn btn-primary mt-2')
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=3),
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Department Filter'),
                    dcc.Dropdown(
                        id='dept-filter',
                        options=[{'label': 'All Departments', 'value': 'all'}] + [{'label': dept, 'value': dept} for dept in
                                                                                dept_names],
                        value='all',
                        multi=True,
                        className='form-control mt-2',
    style={
        'backgroundColor': '#2c2c2c',
        'color': '#ffffff',
        'borderColor': '#4d4d4d'
    }
                    )
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=3, ),
        dbc.Col([
    html.Div([
        html.Div([
            html.H3('Date Range Filter'),
            dcc.DatePickerRange(
                id='date-range-filter',
                start_date=start_date,
                end_date=end_date,
                className='form-control mt-2',
                style={
                    'backgroundColor': '#2c2c2c',
                    'color': '#ffffff',
                    'borderColor': '#4d4d4d'
                },
                start_date_placeholder_text='Start Date',
                end_date_placeholder_text='End Date'
            )
        ], className='card-content')
    ], className='single-card-wrapper')
], width=3),
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Grouping'),
                    dcc.Dropdown(
                        id='grouping',
                        options=[
                            {'label': 'Weekly', 'value': 'weekly'},
                            {'label': 'Monthly', 'value': 'monthly'},
                            {'label': 'Yearly', 'value': 'yearly'}
                        ],
                        value='monthly',
                        className='form-control mt-2',
                        
    style={
        'backgroundColor': '#2c2c2c',
        'color': '#ffffff',
        'borderColor': '#4d4d4d'
    }
                    )
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=3, ),
        dbc.Col([
            html.Div(id='disease-link')  # Added the container here
        ], width=8)
    ]),
    # Cards for patient count, visits, and admissions
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Number of Patients'),
                    html.P(id='patient-count', className='card-value')
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Number of Visits'),
                    html.P(id='visits-count', className='card-value')
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Number of Admissions'),
                    html.P(id='admissions-count', className='card-value')
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id='patient-count-loading',
                type='default',
                children=[
                    dcc.Graph(id='patient-count-chart')
                ]
            )
        ], width=6),
        dbc.Col([
            dcc.Loading(
                id='admissions-loading',
                type='default',
                children=[
                    dcc.Graph(id='admissions-chart')
                ]
            )
        ], width=6)
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px',
              'marginBottom': '20px'}),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id='visits-loading',
                type='default',
                children=[
                    dcc.Graph(id='visits-chart')
                ]
            )
        ], width=6)
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px',
              'marginBottom': '20px'})
], fluid=True)

import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

@dash_app.callback(
    Output('disease-link', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('disease-name-input', 'value')],
    allow_duplicate=True
)
def search_disease(n_clicks, disease_name):
    if not dash.callback_context.triggered:
        raise PreventUpdate
    else:
        trigger_id = dash.callback_context.triggered[0]['prop_id']
        print("GSG")
        print(trigger_id)
        print(n_clicks)
        if trigger_id == 'search-button.n_clicks' and n_clicks > 0:
            disease_data_url = f"http://localhost:5552/dash/?disease_name={disease_name}"
            return html.A(href=disease_data_url, target="_blank", children="Open Disease Data")
        else:
            return None

# Callback functions
@dash_app.callback(
    [
        Output('patient-count-chart', 'figure'),
        Output('admissions-chart', 'figure'),
        Output('visits-chart', 'figure'),
        Output('patient-count', 'children'),
        Output('visits-count', 'children'),
        Output('admissions-count', 'children')
    ],
    [Input('dept-filter', 'value'), Input('date-range-filter', 'start_date'), Input('date-range-filter', 'end_date'), Input('grouping', 'value')]
)
def update_charts(selected_depts, start_date, end_date, grouping):
    if 'all' in selected_depts:
        dept_names = ','.join(requests.get(f"http://localhost:5555/departments").json())
    else:
        dept_names = ','.join(selected_depts)

    start_date = datetime.fromisoformat(start_date).strftime('%Y-%m-%d')
    end_date = datetime.fromisoformat(end_date).strftime('%Y-%m-%d')
    api_url = f"http://localhost:5555/patient_counts?dept_names={dept_names}&start_date={start_date}&end_date={end_date}&grouping={grouping}"
    response = requests.get(api_url)
    data = response.json()
    df = pd.DataFrame(data)

    # Number of Patients
    patient_count_chart = px.line(df[df['col1'] == 'ENCOUNTER'], x='data_date', y='patient_count', color='dept_name')
    patient_count_chart.update_layout(
        title='Number of Patients',
        xaxis_title='Time',
        yaxis_title='Patient Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',  # Set plot background color to dark grey
        paper_bgcolor='rgba(17, 17, 17, 1)',  # Set paper background color to dark grey
        font_color='white',  # Set font color to white
        xaxis_gridcolor='rgba(51, 51, 51, 1)',  # Set grid line color for x-axis
        yaxis_gridcolor='rgba(51, 51, 51, 1)',  # Set grid line color for y-axis
    )

    # Admissions
    admissions_df = df[df['col1'] == 'ADMISSIONS']
    admissions_chart = px.line(admissions_df, x='data_date', y=['rec_count', 'patient_count'], color='dept_name')
    admissions_chart.update_layout(
        title='Admissions',
        xaxis_title='Date',
        yaxis_title='Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)',
    )

    # Visits
    visits_df = df[(df['col1'] == 'ENCOUNTER') | (df['col1'] == 'VISIT')]
    visits_chart = px.line(visits_df, x='data_date', y='rec_count', color='dept_name')
    visits_chart.update_layout(
        title='Visits',
        xaxis_title='Date',
        yaxis_title='Visit Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)',
    )
    total_patients = df[df['col1'] == 'ENCOUNTER']['patient_count'].sum()

    # Calculate total visits
    total_visits = df[df['col1'].isin(['ENCOUNTER', 'VISIT'])]['rec_count'].sum()

    # Calculate total admissions
    total_admissions = df[df['col1'] == 'ADMISSIONS']['rec_count'].sum()
    
    return patient_count_chart, admissions_chart, visits_chart, f'{int(total_patients):,}', f'{int(total_visits):,}', f'{int(total_admissions):,}'

if __name__ == '__main__':
    port = int(os.getenv('DASHBOARD_APP_PORT', 3434))  # Use 3434 as default if the env variable is not set
    dash_app.run_server(port=port, debug=True)