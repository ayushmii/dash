import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State
import json

# Load data from JSON file
with open('patient_data.json', 'r') as f:
    data_dict = json.load(f)

data = pd.DataFrame(data_dict)

# Convert date columns to datetime
date_columns = ['date', 'readmission_date']
for col in date_columns:
    data[col] = pd.to_datetime(data[col], errors='coerce')

# Create the Dash app
app = Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1('Patient Records Dashboard', style={'color': 'white', 'textAlign': 'center'}),

    # Department Filter
    html.Div([
        html.H3('Department', style={'color': 'white'}),
        dcc.Dropdown(
            id='dept-dropdown',
            options=[{'label': dept, 'value': dept} for dept in data['department'].unique()],
            value=data['department'].unique()[0],
            multi=True,
            style={'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'color': 'white'}
        )
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'margin': '10px'}),

    # Date Duration Filter
    html.Div([
        html.H3('Data Duration', style={'color': 'white'}),
        dcc.DatePickerRange(
            id='date-range-picker',
            display_format='MMM YY',
            start_date=data['date'].min(),
            end_date=data['date'].max(),
            calendar_orientation='horizontal',
            style={'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'color': 'white', 'margin': '5px'}
        )
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'margin': '10px'}),

    # Display selected filters
    html.Div(id='selected-filters', style={'color': 'white', 'margin': '10px'}),

    # Additional charts
    html.Div([
        html.H3('Additional Charts', style={'color': 'white', 'textAlign': 'center'}),
        html.Div([
            html.H4('Caregiver Count', style={'color': 'white', 'marginBottom': '5px'}),
            dcc.Graph(id='caregiver-count-chart', figure={})
        ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'margin': '10px'}),
        html.Div([
            html.H4('Location Count', style={'color': 'white', 'marginBottom': '5px'}),
            dcc.Graph(id='location-count-chart', figure={})
        ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'margin': '10px'}),
        html.Div([
            html.H4('Inpatient vs Outpatient', style={'color': 'white', 'marginBottom': '5px'}),
            dcc.Graph(id='inpatient-outpatient-chart', figure={})
        ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'margin': '10px'})
    ]),

    # Patient Data
    html.Div([
        html.H3('Patient Data', style={'color': 'white'}),
        html.Div(id='patient-data', style={'color': 'white', 'padding': '5px'})
    ], style={'backgroundColor': 'rgba(30, 30, 30, 0.8)', 'padding': '10px', 'borderRadius': '5px', 'margin': '10px'}),

    # Charts (initially empty)
    dcc.Graph(id='patient-count-chart', figure={}),
    dcc.Graph(id='total-counts-chart', figure={}),
    dcc.Graph(id='prescription-count-chart', figure={}),
    dcc.Graph(id='lab-results-chart', figure={}),
    dcc.Graph(id='admission-visit-chart', figure={}),
    html.Div(id='avg-length-of-stay', style={'color': 'white', 'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'padding': '10px', 'borderRadius': '5px'}),
    html.Div(id='staff-patient-ratio', style={'color': 'white', 'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'padding': '10px', 'borderRadius': '5px'}),
    html.Div(id='mortality-rate', style={'color': 'white', 'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'padding': '10px', 'borderRadius': '5px'}),
    html.Div(id='ot-utilization', style={'color': 'white', 'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'padding': '10px', 'borderRadius': '5px'}),
    html.Div(id='readmission-rate', style={'color': 'white', 'backgroundColor': 'rgba(50, 50, 50, 0.8)', 'padding': '10px', 'borderRadius': '5px'})
], style={'backgroundColor': 'rgba(20, 20, 20, 0.8)', 'padding': '20px'})

# Define the callbacks
@app.callback(
    [Output('patient-data', 'children'),
     Output('patient-count-chart', 'figure'),
     Output('total-counts-chart', 'figure'),
     Output('prescription-count-chart', 'figure'),
     Output('lab-results-chart', 'figure'),
     Output('admission-visit-chart', 'figure'),
     Output('avg-length-of-stay', 'children'),
     Output('staff-patient-ratio', 'children'),
     Output('mortality-rate', 'children'),
     Output('ot-utilization', 'children'),
     Output('readmission-rate', 'children'),
     Output('caregiver-count-chart', 'figure'),
     Output('location-count-chart', 'figure'),
     Output('inpatient-outpatient-chart', 'figure'),
     Output('selected-filters', 'children')],
    [Input('dept-dropdown', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_dashboard(selected_depts, start_date, end_date):
    # Filter data based on selected departments
    filtered_data = data[data['department'].isin(selected_depts)]

    # Filter data based on date range
    filtered_data = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

    # Calculate patient data
    patient_count = filtered_data['numPatients'].sum()
    admissions = filtered_data['numAdmissions'].sum()
    visits = filtered_data['numVisits'].sum()
    outpatients = filtered_data['numOutpatients'].sum()
    discharge_summary = filtered_data['numDischargeSummaries'].sum()

    # Create charts
    patient_count_chart = go.Figure(data=[go.Scatter(x=filtered_data['date'], y=filtered_data['numPatients'], mode='lines')])
    total_counts_chart = go.Figure(data=[go.Scatter(x=filtered_data['date'], y=filtered_data['numPatients'], mode='lines')])
    prescription_count_chart = go.Figure(data=[go.Scatter(x=filtered_data['date'], y=filtered_data['numPrescriptions'], mode='lines')])
    lab_results_chart = go.Figure(data=[go.Scatter(x=filtered_data['date'], y=filtered_data['numLabResults'], mode='lines')])

    # Calculate additional data
    avg_length_of_stay = f"Average Length of Stay: {filtered_data['length_of_stay'].mean()} days"
    staff_patient_ratio = f"Staff-Patient Ratio: {filtered_data['staff_count'].sum() / patient_count:.2f}"
    mortality_rate = f"Mortality Rate: {(filtered_data[filtered_data['discharge_disposition'] == 'Expired'].shape[0] / patient_count) * 100:.2f}%"
    ot_utilization = f"OT Utilization: {filtered_data['ot_utilization'].mean():.2f}"
    readmission_rate = f"Readmission Rate: {(filtered_data['readmission_date'].notnull().sum() / patient_count) * 100:.2f}%"

    # Additional charts (placeholder)
    caregiver_count_chart = go.Figure()
    location_count_chart = go.Figure()
    inpatient_outpatient_chart = go.Figure()

    # Display selected filters
    selected_filters_text = f"Selected Departments: {', '.join(selected_depts)}\nDate Range: {start_date} to {end_date}"

    return (
        [f"Number of Patients: {patient_count}",
         f"Admissions: {admissions}",
         f"Visits: {visits}",
         f"Outpatients: {outpatients}",
         f"Discharge Summary: {discharge_summary}"],
        patient_count_chart,
        total_counts_chart,
        prescription_count_chart,
        lab_results_chart,
        admission_visit_chart,
        avg_length_of_stay,
        staff_patient_ratio,
        mortality_rate,
        ot_utilization,
        readmission_rate,
        caregiver_count_chart,
        location_count_chart,
        inpatient_outpatient_chart,
        selected_filters_text
    )

if __name__ == '__main__':
    app.run_server(debug=True)

