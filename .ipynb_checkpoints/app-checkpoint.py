import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State
import json

# Load data from JSON file
with open('patient_data.json', 'r') as f:
    data_dict = json.load(f)

data = pd.DataFrame([
    {'date': datetime.strptime(d['date'], '%Y-%m-%d'), 'department': d['department'], 'numPatients': d['numPatients'],
     'numAdmissions': d['numAdmissions'], 'numVisits': d['numVisits'], 'numOutpatients': d['numOutpatients'],
     'numDischargeSummaries': d['numDischargeSummaries'], 'numPrescriptions': d['numPrescriptions'],
     'numLabResults': d['numLabResults']}
    for d in data_dict
])

# Create the Dash app
app = Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1('Patient Records Dashboard'),
    
    # Department Filter
    html.Div([
        html.H3('Department'),
        dcc.Dropdown(
            id='dept-dropdown',
            options=[{'label': dept, 'value': dept} for dept in data['department'].unique()],
            value=data['department'].unique()[0],
            multi=True
        )
    ]),
    
    # Date Duration Filter
    html.Div([
        html.H3('Data Duration'),
        dcc.RadioItems(
            id='date-duration',
            options=[
                {'label': '2010-2019', 'value': '2010-2019'},
                {'label': 'Jan 2010-Dec 2019', 'value': 'jan2010-dec2019'},
                {'label': '2017', 'value': '2017'},
                {'label': 'June, 2017', 'value': 'jun2017'}
            ],
            value='2010-2019'
        ),
        html.Button('Change Date Range', id='date-range-btn'),
        dcc.DatePickerRange(
            id='date-range-picker',
            display_format='MMM YY',
            start_date_placeholder_text='Start Period',
            end_date_placeholder_text='End Period',
            calendar_orientation='horizontal'
        )
    ]),
    
    # Display selected filters
    html.Div(id='selected-filters'),
    
    # Patient Data
    html.Div([
        html.H3('Patient Data'),
        html.Div(id='patient-data')
    ]),
    
    # Charts
    dcc.Graph(id='patient-count-chart'),
    dcc.Graph(id='total-counts-chart'),
    dcc.Graph(id='prescription-count-chart'),
    dcc.Graph(id='lab-results-chart'),
    dcc.Graph(id='admission-visit-chart'),
    
    # Additional boxes
    html.Div(id='avg-length-of-stay'),
    html.Div(id='staff-patient-ratio'),
    html.Div(id='mortality-rate'),
    html.Div(id='ot-utilization'),
    html.Div(id='readmission-rate'),
    
    # Additional charts
    dcc.Graph(id='caregiver-count-chart'),
    dcc.Graph(id='location-count-chart'),
    dcc.Graph(id='inpatient-outpatient-chart')
])

# Define the callbacks
# ... (same as before)

if __name__ == '__main__':
    app.run_server(debug=True)