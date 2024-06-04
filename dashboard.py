import os
from dash import Dash, dcc, html, Input, Output, State
from datetime import datetime
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flask import Flask
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import dotenv_values

env_vars = dotenv_values('.env')  # take environment variables from .env.

styles_path = 'styles.css'  # If the file is in the same directory as your Python script
# styles_path = 'path/to/styles.css'  # If the file is in a different directory

# Check if the file exists
if os.path.isfile(styles_path):
    print(f"The file '{styles_path}' exists.")
    # You can perform additional operations here, such as reading the file contents
    with open(styles_path, 'r') as file:
        print("Opened")
else:
    print(f"The file '{styles_path}' does not exist.")

# Flask app and Dash app
app = Flask(__name__)
dash_app = Dash(server=app, routes_pathname_prefix='/dash/', external_stylesheets=[styles_path, dbc.themes.BOOTSTRAP])

# Default date range
start_date = datetime(2010, 1, 1)
end_date = datetime(2019, 12, 31)

# Fetch department names
dept_names = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/departments").json()

# Dash layout
dash_app.layout = dbc.Container([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="assets/logo.png", className="logo"),
                    html.H1("Sanjay Gandhi Postgraduate Institute of Medical Sciences", className="header-title")
                ], className="header-container", style={
                    'border-radius': '10px'
                })
            ], width=12)
        ]),
    ]),html.Div(id='selected-filters', style={'color': 'white', 'fontSize': '18px', 'textAlign': 'center'}),
    dbc.Modal(
    [
        dbc.ModalHeader("Filters"),
        dbc.ModalBody([
            html.Div([
                html.H3('Department', className='h3-center', style={"color": "white"}),
                dcc.Dropdown(
                    id='dept-filter',
                    options=[{'label': 'All Departments', 'value': 'all'}] + [{'label': dept, 'value': dept} for dept in dept_names],
                    value='all',
                    multi=True,
                    className='form-control mt-2 custom-dropdown',
                )
            ], className='p-2', style={'overflow': 'visible'}),
            html.Div([
                html.H3('Date Range', className='h3-center', style={"color": "white"}),
                dcc.DatePickerRange(
                    id='date-range-filter',
                    start_date=start_date,
                    end_date=end_date,
                    className='form-control mt-2 w-70',
                    style={
                        'backgroundColor': '#2c2c2c',
                        'color': '#ffffff',
                        'borderColor': '#4d4d4d',
                        'text-align': 'center'
                    },
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date',
                    display_format='DD/MM/YYYY'
                )
            ], className='p-2'),
            html.Div([
                html.H3('Grouping', className='h3-center', style={"color": "white"}),
                dcc.Dropdown(
                    id='grouping',
                    options=[
                        {'label': 'Weekly', 'value': 'weekly'},
                        {'label': 'Monthly', 'value': 'monthly'},
                        {'label': 'Yearly', 'value': 'yearly'}
                    ],
                    value='monthly',
                    className='form-control mt-2 custom-dropdown',
                )
            ], className='p-2', style={'overflow': 'visible'})
        ]),
        dbc.ModalFooter(
            dbc.Button("Search", id="search-button", className="ml-auto", n_clicks=0)
        ),
    ],
    id="modal",
    is_open=False,
),dbc.Button("Open Filters", id="open-modal-button", n_clicks=0),
    # Cards for patient count, visits, and admissions
    dbc.Row([
        dbc.Col([
            html.H3("Patient Statistics", style={"color": "white"}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Patients'),
                    html.P(id='patient-count', className='card-value', style={'fontSize': '50px !important'})
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Visits'),
                    html.P(id='visits-count', className='card-value', style={'fontSize': '50px !important'})
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=4),
        dbc.Col([
            html.Div([
                html.Div([
                    html.H3('Admissions'),
                    html.P(id='admissions-count', className='card-value', style={'fontSize': '50px !important'})
                ], className='card-content')
            ], className='single-card-wrapper')
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Patient Count and Admissions", style={"color": "white"}),
        ], width=12),
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
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '20px'}),
    dbc.Row([
        dbc.Col([
            html.H3("Visits and Caregivers", style={"color": "white"}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id='visits-loading',
                type='default',
                children=[
                    dcc.Graph(id='visits-chart')
                ]
            )
        ], width=6),
        dbc.Col([
            dcc.Loading(
                id='caregiver-chart-loading',
                type='default',
                children=[
                    dcc.Graph(id='caregiver-chart')
                ]
            )
        ], width=6)
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '20px'}),
    dbc.Row([
        dbc.Col([
            html.H3("Prescriptions", style={"color": "white"}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id='prescriptions-loading',
                type='default',
                children=[
                    dcc.Graph(id='prescriptions-chart')
                ]
            )
        ], width=6),
        dbc.Col([
            dcc.Loading(
                id='prescriptions-dept-loading',
                type='default',
                children=[
                    dcc.Graph(id='prescriptions-dept-chart')
                ]
            )
        ], width=6),
        dcc.Store(id='selected-month-store-pres', data='') 
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '20px'}),
    dbc.Row([
        dbc.Col([
            html.H3("Lab Orders", style={"color": "white"}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id='lab-orders-loading',
                type='default',
                children=[
                    dcc.Graph(id='lab-orders-chart')]
           )
       ], width=6),
       dbc.Col([
           dcc.Loading(
               id='lab-orders-dept-loading',
               type='default',
               children=[
                   dcc.Graph(id='lab-orders-dept-chart')
               ]
           )
       ], width=6),
       dcc.Store(id='selected-month-store', data='')  # Add this line
   ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '20px'}),
   dbc.Row([
       dbc.Col([
           html.H3("Admission Length", style={"color": "white"}),
       ], width=12),
   ]),
   dbc.Row([
       dbc.Col([
           dcc.Loading(
               id='admission-length-loading',
               type='default',
               children=[
                   dcc.Graph(id='admission-length-chart')
               ]
           )
       ], width=12),
       dbc.Col([
           html.P(id='admission-length-stats', style={'color': 'white', 'fontSize': '18px', 'textAlign': 'center'})
       ], width=12)
   ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '20px'})
, dbc.Row([
        dbc.Col([
            html.A(
                html.Img(
                    src="assets/search.png",
                    id="open-new-tab-image",
                    className="fixed-image",
                    style={"width": "100px", "transition": "transform 0.3s ease"},
                ),
                href="localhost:3000",  # Replace with the desired URL
                target="_blank",
                style={"position": "fixed", "bottom": "40px", "right": "40px", "zIndex": "9999"},
            )
        ], width=12)
    ])
], fluid=True, id='body')


import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

@dash_app.callback(
    Output('body', 'className'),
    [Input('grouping', 'value')]
)
def toggle_dropdown_open(value):
    if not dash.callback_context.triggered:
        raise PreventUpdate
    else:
        ctx = dash.callback_context
        if ctx.triggered_id == 'grouping':
            prop_id = ctx.triggered_prop_id
            if prop_id == 'grouping.value':
                # Dropdown menu opened
                return 'dropdown-open'
            else:
                # Dropdown menu closed
                return ''
        else:
            raise PreventUpdate

import plotly.express as px

import plotly.express as px

def fetch_caregiver_data():
    try:
        response = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/Caregiver.json")
        response.raise_for_status()
        data = response.json()
        return data["departments"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching caregiver data: {e}")
        return []

def prepare_bar_chart_data(caregiver_data):
    df = pd.DataFrame(caregiver_data)
    return df

import plotly.express as px

def fetch_caregiver_data():
    try:
        response = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/Caregiver.json")
        response.raise_for_status()
        data = response.json()
        return data["departments"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching caregiver data: {e}")
        return []

def prepare_bar_chart_data(caregiver_data):
    df = pd.DataFrame(caregiver_data)
    return df

@dash_app.callback(
    Output('caregiver-chart', 'figure'),
    Input('dept-filter', 'value')
)
def update_caregiver_chart(selected_depts):
    caregiver_data = fetch_caregiver_data()
    df = prepare_bar_chart_data(caregiver_data)

    if 'all' not in selected_depts:
        df = df[df['department_name'].isin(selected_depts)]

    cg_types = df['cg_type'].unique()
    colors = px.colors.qualitative.Vivid[:len(cg_types)]  # Choose a color palette

    fig = go.Figure()

    # Calculate department-wise totals
    dept_totals = df.groupby('department_name')['count'].sum().to_dict()

    for cg_type, color in zip(cg_types, colors):
        cg_type_df = df[df['cg_type'] == cg_type]
        fig.add_trace(go.Bar(
            x=cg_type_df['department_name'],
            y=cg_type_df['count'],
            name=cg_type,
            marker_color=color,
            hovertext=[f"Department Total: {dept_totals[dept]}" for dept in cg_type_df['department_name']],  # Add hovertext for department-wise total
            hovertemplate="<b>%{x}</b><br>Count: %{y}<br>%{hovertext}<extra></extra>"  # Customize hover template
        ))

    fig.update_layout(
        title='Number of Caregivers by Department and Type',
        xaxis_title='Department',
        yaxis_title='Number of Caregivers',
        barmode='stack',
        legend_title='Caregiver Type',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)'
    )

    return fig

@dash_app.callback(
    Output("modal", "is_open"),
    [Input("open-modal-button", "n_clicks"), Input("search-button", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@dash_app.callback(
    Output('selected-month-store', 'data'),
    Input('lab-orders-chart', 'clickData')
)
def update_selected_month(click_data):
    if click_data:
        selected_month = click_data['points'][0]['x']
        return selected_month
    else:
        return ''
# Callback functions

@dash_app.callback(
    [
        Output('lab-orders-chart', 'figure'),
        Output('lab-orders-dept-chart', 'figure')
    ],
    [ Input('dept-filter', 'value'), Input('date-range-filter', 'start_date'), Input('date-range-filter', 'end_date'), Input('grouping', 'value'),Input('selected-month-store', 'data')]
)
def update_charts_lab(selected_depts, start_date, end_date, grouping,selected_month):
    if 'all' in selected_depts:
        dept_names = ','.join(requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/departments").json())
    else:
        dept_names = ','.join(selected_depts)

    prescription_data = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/prescription.json").json()["departments"]
    
    start_date = datetime.fromisoformat(start_date).strftime('%Y-%m-%d')
    end_date = datetime.fromisoformat(end_date).strftime('%Y-%m-%d')

    # Filter department-wise lab orders data if a month is selected
    lab_orders_data = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/laborders.json").json()["departments"]

    # Prepare overall lab orders data
    overall_lab_orders = pd.DataFrame([
        {"month": entry["month"], "count": entry["count"]}
        for dept in lab_orders_data
        for entry in dept["lab_orders"]
    ])
    overall_lab_orders = overall_lab_orders.groupby("month")["count"].sum().reset_index()

    # Sort overall lab orders data by month
    overall_lab_orders['month'] = pd.to_datetime(overall_lab_orders['month'])
    overall_lab_orders = overall_lab_orders.sort_values('month')

    # Prepare department-wise lab orders data
    dept_lab_orders = pd.DataFrame([
        {"department_name": dept["department_name"], "month": entry["month"], "count": entry["count"]}
        for dept in lab_orders_data
        for entry in dept["lab_orders"]
    ])

    # Create the overall lab orders chart
    lab_orders_chart = go.Figure()
    lab_orders_chart.add_trace(go.Bar(
        x=overall_lab_orders["month"],
        y=overall_lab_orders["count"],
        marker_color='rgb(26, 118, 255)'
    ))
    lab_orders_chart.update_layout(
        title='Overall',
        xaxis_title='Month',
        yaxis_title='Lab Order Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)'
    )
    
    if selected_month:
        dept_lab_orders = dept_lab_orders[dept_lab_orders['month'] == selected_month]

    # Sort department-wise lab orders data by month
    dept_lab_orders['month'] = pd.to_datetime(dept_lab_orders['month'])
    dept_lab_orders = dept_lab_orders.sort_values('month')

    # Create the department-wise lab orders chart
    lab_orders_dept_chart = go.Figure()
    for dept_name, group in dept_lab_orders.groupby("department_name"):
        lab_orders_dept_chart.add_trace(go.Bar(
            x=group["month"],
            y=group["count"],
            name=dept_name
        ))
    lab_orders_dept_chart.update_layout(
        title='By Department',
        xaxis_title='Month',
        yaxis_title='Lab Order Count',
        barmode='group',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return (
        lab_orders_chart, lab_orders_dept_chart
    )

@dash_app.callback(
    [
        Output('prescriptions-chart', 'figure'),
        Output('prescriptions-dept-chart', 'figure'),
        Output('selected-month-store-pres', 'data')
    ],
    [
        Input('dept-filter', 'value'),
        Input('date-range-filter', 'start_date'),
        Input('date-range-filter', 'end_date'),
        Input('grouping', 'value'),
        Input('prescriptions-chart', 'clickData')
    ]
)
def update_charts_pres(selected_depts, start_date, end_date, grouping, click_data):
    if 'all' in selected_depts:
        dept_names = ','.join(requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/departments").json())
    else:
        dept_names = ','.join(selected_depts)

    prescription_data = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/prescription.json").json()["departments"]
    start_date = datetime.fromisoformat(start_date).strftime('%Y-%m-%d')
    end_date = datetime.fromisoformat(end_date).strftime('%Y-%m-%d')

    overall_prescriptions = pd.DataFrame([
        {"month": entry["month"], "count": entry["count"]}
        for dept in prescription_data
        for entry in dept["prescription_count"]
    ])
    overall_prescriptions = overall_prescriptions.groupby("month")["count"].sum().reset_index()

    # Sort overall prescriptions data by month
    overall_prescriptions['month'] = pd.to_datetime(overall_prescriptions['month'])
    overall_prescriptions = overall_prescriptions.sort_values('month')

    dept_prescriptions = pd.DataFrame([
        {"department_name": dept["department_name"], "month": entry["month"], "count": entry["count"]}
        for dept in prescription_data
        for entry in dept["prescription_count"]
    ])

    selected_month = None
    if click_data:
        selected_month = click_data['points'][0]['x']

    # Create the overall prescriptions chart
    prescriptions_chart = go.Figure()
    prescriptions_chart.add_trace(go.Bar(
        x=overall_prescriptions["month"],
        y=overall_prescriptions["count"],
        marker_color='rgb(132, 224, 130)'
    ))
    prescriptions_chart.update_layout(
        title='Overall',
        xaxis_title='Month',
        yaxis_title='Prescription Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)'
    )

    # Create the department-wise prescriptions chart
    prescriptions_dept_chart = go.Figure()
    if selected_month:
        dept_prescriptions = dept_prescriptions[dept_prescriptions["month"] == selected_month]

    dept_counts = dept_prescriptions.groupby("department_name")["count"].sum().reset_index()
    prescriptions_dept_chart.add_trace(go.Pie(
        labels=dept_counts["department_name"],
        values=dept_counts["count"],
        hole=.3
    ))
    prescriptions_dept_chart.update_layout(
        title='By Department',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white'
    )

    return prescriptions_chart, prescriptions_dept_chart, selected_month
import pandas as pd
import numpy as np
import plotly.figure_factory as ff

def compute_admission_length_stats(start_date, end_date):
    admission_data = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/admission.json").json()["admissions"]
    
    admission_lengths = []

    for admission in admission_data:
        admission_date = datetime.fromisoformat(admission["admission_date"])
        discharge_date = datetime.fromisoformat(admission["discharge_date"])
        print(admission_date)
        print(discharge_date)
        admission_length = (discharge_date - admission_date).days

        if start_date <= admission_date <= end_date:
            admission_lengths.append(admission_length)
    print(admission_lengths)
    if not admission_lengths:
        return None

    admission_lengths_df = pd.DataFrame({'admission_length': admission_lengths})
    mean_length = admission_lengths_df['admission_length'].mean()
    median_length = admission_lengths_df['admission_length'].median()
    std_length = admission_lengths_df['admission_length'].std()

    fig = ff.create_distplot([admission_lengths_df['admission_length']], ['Admission Length'], bin_size=1)
    fig.add_vline(x=mean_length, line_width=2, line_dash="dash", line_color="green", annotation_text=f"Mean: {mean_length:.2f}")
    fig.add_vline(x=median_length, line_width=2, line_dash="dash", line_color="red", annotation_text=f"Median: {median_length:.2f}")

    fig.update_layout(
        title='Admission Length Density Plot',
        xaxis_title='Admission Length (days)',
        yaxis_title='Density',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)'
    )

    return fig, mean_length, median_length, std_length

@dash_app.callback(
    [
        Output('admission-length-chart', 'figure'),
        Output('admission-length-stats', 'children')
    ],
    [Input('dept-filter', 'value'), Input('date-range-filter', 'start_date'), Input('date-range-filter', 'end_date')]
)
def update_admission_length_chart(selected_depts, start_date, end_date):
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    stats = compute_admission_length_stats(start_date, end_date)

    if stats is None:
        return go.Figure(), ''

    fig, mean_length, median_length, std_length = stats

    stats_text = f"Mean: {mean_length:.2f} days | Median: {median_length:.2f} days | Std. Dev: {std_length:.2f} days"

    return fig, stats_text

@dash_app.callback(
    Output('selected-filters', 'children'),
    [Input('dept-filter', 'value'), Input('date-range-filter', 'start_date'), Input('date-range-filter', 'end_date'), Input('grouping', 'value')]
)
def update_selected_filters(selected_depts, start_date, end_date, grouping):
    if 'all' in selected_depts:
        dept_text = 'All Departments'
    else:
        dept_text = ', '.join(selected_depts)
    
    start_date = datetime.fromisoformat(start_date).strftime('%d/%m/%Y')
    end_date = datetime.fromisoformat(end_date).strftime('%d/%m/%Y')
    
    return f'Selected Filters: Departments: {dept_text} | Date Range: {start_date} - {end_date} | Grouping: {grouping.capitalize()}'

@dash_app.callback(
    [
        Output('patient-count-chart', 'figure'),
        Output('admissions-chart', 'figure'),
        Output('visits-chart', 'figure'),
        Output('patient-count', 'children'),
        Output('visits-count', 'children'),
        Output('admissions-count', 'children')
       
    ],
    [[Input("search-button", "n_clicks")]],
    [
        State('dept-filter', 'value'),
        State('date-range-filter', 'start_date'),
        State('date-range-filter', 'end_date'),
        State('grouping', 'value')
    ]
)
def update_charts(n_clicks,selected_depts, start_date, end_date, grouping):
    if 'all' in selected_depts:
        dept_names = ','.join(requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/departments").json())
    else:
        dept_names = ','.join(selected_depts)

    prescription_data = requests.get(f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/get-json/prescription.json").json()["departments"]
    
    start_date = datetime.fromisoformat(start_date).strftime('%Y-%m-%d')
    end_date = datetime.fromisoformat(end_date).strftime('%Y-%m-%d')
    api_url = f"http://localhost:{os.getenv('QUERRY_SERVER_PORT', 7655)}/patient_counts?dept_names={dept_names}&start_date={start_date}&end_date={end_date}&grouping={grouping}"
    response = requests.get(api_url)
    data = response.json()
    df = pd.DataFrame(data)
    df = df.sort_values('data_from', ascending=True)

    print(start_date)
    print(end_date)
    print(df.columns)
    patient_count_chart = px.line(df[df['col1'] == 'ENCOUNTER_VISIT'], x='data_date', y='patient_count', color='dept_name')
    total_patient_count = df[df['col1'] == 'ENCOUNTER_VISIT'].groupby('data_date')['patient_count'].sum().reset_index()
    patient_count_chart.add_trace(go.Scatter(x=total_patient_count['data_date'], y=total_patient_count['patient_count'], mode='lines', name='Total', line=dict(color='white', width=2)))
    patient_count_chart.update_layout(
        title='Patients',
        xaxis_title='Time',
        yaxis_title='Patient Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',  # Set plot background color to dark grey
        paper_bgcolor='rgba(17, 17, 17, 1)',  # Set paper background color to dark grey
        font_color='white',  # Set font color to white
        xaxis_gridcolor='rgba(51, 51, 51, 1)',  # Set grid line color for x-axis
        yaxis_gridcolor='rgba(51, 51, 51, 1)',  # Set grid line color for y-axis
        legend=dict(orientation="h", yanchor="bottom", y=1.00, xanchor="right",title='Departments', x=1)

    )

    # Admissions
    admissions_df = df[df['col1'] == 'ADMISSIONS']
    print(admissions_df)

    admissions_chart = go.Figure()

    # Add a bar trace for rec_count
    admissions_chart.add_trace(go.Bar(
        x=admissions_df['data_date'],
        y=admissions_df['rec_count'],
        name='Admission Count',
        marker_color='rgb(55, 83, 109)'  # Set the color for the bars
    ))

    # Add a bar trace for patient_count
    admissions_chart.add_trace(go.Bar(
        x=admissions_df['data_date'],
        y=admissions_df['patient_count'],
        name='Patient Count',
        marker_color='rgb(26, 118, 255)'  # Set a different color for the bars
    ))

    # Calculate the total rec_count and add it as a separate trace
    total_admissions_count = admissions_df.groupby('data_date')['rec_count'].sum().reset_index()
    admissions_chart.add_trace(go.Scatter(
        x=total_admissions_count['data_date'],
        y=total_admissions_count['rec_count'],
        mode='lines',
        name='Total Admission Count',
        line=dict(color='white', width=2)
    ))

    admissions_chart.update_layout(
        title='Admissions',
        xaxis_title='Date',
        yaxis_title='Count',
        barmode='group',  # Group bars for each date
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Visits
    visits_df = df[(df['col1'] == 'ENCOUNTER_VISIT')]

    visits_chart = go.Figure()

    # Add area traces for each department
    for dept_name, group in visits_df.groupby('dept_name'):
        visits_chart.add_trace(go.Scatter(
            x=group['data_date'],
            y=group['rec_count'],
            mode='lines',
            stackgroup='one',
            name=dept_name,
            fill='tozeroy'  # Fill the area under the line
        ))

    # Add a trace for the total visits count
    total_visits_count = visits_df.groupby('data_date')['rec_count'].sum().reset_index()
    visits_chart.add_trace(go.Scatter(
        x=total_visits_count['data_date'],
        y=total_visits_count['rec_count'],
        mode='lines',
        name='Total',
        line=dict(color='white', width=2)
    ))

    visits_chart.update_layout(
        title='Visits',
        xaxis_title='Date',
        yaxis_title='Visit Count',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(17, 17, 17, 1)',
        font_color='white',
        xaxis_gridcolor='rgba(51, 51, 51, 1)',
        yaxis_gridcolor='rgba(51, 51, 51, 1)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right",title="Departments", x=1)
    )

    total_patients = df[df['col1'] == 'ENCOUNTER_VISIT']['patient_count'].sum()

    # Calculate total visits
    total_visits = df[df['col1'] == 'ENCOUNTER_VISIT']['rec_count'].sum()

    # Calculate total admissions
    total_admissions = df[df['col1'] == 'ADMISSIONS']['rec_count'].sum()
    
   
    return (
        patient_count_chart, admissions_chart, visits_chart,
        f'{int(total_patients):,}', f'{int(total_visits):,}', f'{int(total_admissions):,}'
    )

import subprocess
import signal

 # Use 3434 as default if the env variable is not set
def kill_subprocesses():
    """Function to kill all subprocesses."""
    for process in subprocesses:
        process.terminate()
    print("All subprocesses terminated.")
    os.kill(os.getpid(), signal.SIGINT)  # Raise KeyboardInterrupt to exit the main program

subprocesses = []

if __name__ == '__main__':
    port = int(os.getenv('DASHBOARD_APP_PORT', 3434)) 
    commands = []

    # Run each command using subprocess
    for cmd in commands:
        try:
            process = subprocess.Popen(cmd, shell=True)
            subprocesses.append(process)
        except Exception as e:
            print(f"Error running command '{cmd}': {e}")
            kill_subprocesses()

    # After running all commands, start the dash app
    try:
        print("PORT IS")
        print(env_vars.get('REACT_APP_DASHBOARD_APP_PORT'))
        port = int(env_vars.get('REACT_APP_DASHBOARD_APP_PORT', 5858))
        dash_app.run_server(port=port, debug=True)
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Closing all programs.")
        kill_subprocesses()
    #dash_app.run_server(port=port)