from flask import Flask, request, jsonify, abort
import os
import cx_Oracle
import requests
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env.

app = Flask(__name__)
CORS(app)

# Database connection
oracle_dsn = cx_Oracle.makedsn("localhost", "1521", service_name="orclpdb1")
conn = cx_Oracle.connect(user="ayush", password="aysh7139", dsn=oracle_dsn)
cur = conn.cursor()

@app.route('/patient_counts', methods=['GET'])
def get_patient_counts():
    dept_names = request.args.get('dept_names', '').split(',')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    grouping = request.args.get('grouping', 'monthly')  # Default to monthly

    # Prepare the SQL query
    query = """
        SELECT
            CASE WHEN col1 IN ('ENCOUNTER', 'VISIT') THEN 'ENCOUNTER_VISIT' ELSE col1 END AS col1_modified,
            dept,
            TRUNC(data_date, :grouping) AS data_date,
            MIN(data_date) AS data_from,
            MAX(data_date) AS data_upto,
            COUNT(*) AS rec_count,
            COUNT(DISTINCT deidpref) AS patient_count,
            (SELECT d.department_name FROM HISDEPARTMENT d WHERE d.department_id = M_PATIENT_COUNTS.dept) AS dept_name
        FROM
            M_PATIENT_COUNTS
        WHERE
            data_date BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
            AND (SELECT d.department_name FROM HISDEPARTMENT d WHERE d.department_id = M_PATIENT_COUNTS.dept) IN (:dept_names)
        GROUP BY
            CASE WHEN col1 IN ('ENCOUNTER', 'VISIT') THEN 'ENCOUNTER_VISIT' ELSE col1 END,
            dept,
            TRUNC(data_date, :grouping)
        ORDER BY
            dept, col1_modified
    """

    # Prepare the grouping function and clause based on the grouping parameter
    grouping_func = 'MONTH' if grouping == 'monthly' else 'YEAR' if grouping == 'yearly' else 'WEEK' if grouping == 'weekly' else None
    if not grouping_func:
        return jsonify({'error': 'Invalid grouping parameter'}), 400

    cur.execute(query, {
        'grouping': grouping_func,
        'start_date': start_date,
        'end_date': end_date,
        'dept_names': tuple(dept_names)
    })

    rows = cur.fetchall()
    data = [
        {
            'col1': row[0],
            'dept': row[1],
            'data_date': row[2].isoformat(),
            'data_from': row[3].isoformat(),
            'data_upto': row[4].isoformat(),
            'rec_count': row[5],
            'patient_count': row[6],
            'dept_name': row[7]
        }
        for row in rows
    ]

    return jsonify(data)

import json

@app.route('/get-json/<filename>', methods=['GET'])
def get_json(filename):
    file_path = os.path.join('data', filename)
    if not os.path.isfile(file_path):
        abort(404, description=f"File {filename} not found")

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        abort(400, description=f"File {filename} is not a valid JSON")
    except Exception as e:
        abort(500, description=f"Error reading {filename}: {str(e)}")
    
    return jsonify(data)

@app.route('/departments', methods=['GET'])
def get_department_names():
    try:
        cur.execute("SELECT department_name FROM HISDEPARTMENT")
        rows = cur.fetchall()
        department_names = [row[0] for row in rows]
        return jsonify(department_names)
    except cx_Oracle.DatabaseError as e:
        error_message = "Database error: {}".format(e)
        return jsonify({"error": error_message}), 500
    except Exception as e:
        error_message = "Error: {}".format(e)
        return jsonify({"error": error_message}), 500

@app.route('/disease_counts', methods=['GET'])
def get_disease_counts():
    disease_name = request.args.get('disease_name')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if not disease_name:
        return jsonify({'error': 'Disease name is required'}), 400

    synonyms = get_synonyms(disease_name)
    query, params = construct_query(disease_name, synonyms)
    results = execute_query(query, params)
    return jsonify(results)

def get_synonyms(disease_name):
    base_url = 'https://uts-ws.nlm.nih.gov/rest'
    endpoint = '/search/current'
    params = {
        'apiKey': '4460d46d-6916-47f4-95aa-e5cf407f9773',
        'string': disease_name
    }

    response = requests.get(f'{base_url}{endpoint}', params=params)
    if response.status_code == 200:
        data = response.json()
        synonyms = []
        if 'result' in data and 'results' in data['result']:
            for result in data['result']['results']:
                if 'name' in result and result['name'] != disease_name:
                    synonyms.append(result['name'])
        return synonyms
    else:
        return []

def construct_query(disease_name, synonyms):
    disease_name_pattern = f"%{disease_name.lower().replace(' ', '')}%"
    synonym_patterns = [f"%{syn.lower().replace(' ', '')}%" for syn in synonyms]

    query = """
        SELECT COUNT(*) AS visits, 23 AS patients, 9 AS discharge_summaries, 4 AS ds_patients
        FROM disease_record
        WHERE
            LOWER(REPLACE(disease_name, ' ', '')) LIKE :disease_name_pattern
            OR LOWER(REPLACE(disease_desc, ' ', '')) LIKE :disease_name_pattern
    """

    if synonym_patterns:
        synonym_conditions = " OR ".join([f"LOWER(REPLACE(disease_desc, ' ', '')) LIKE :syn_{i}" for i in range(len(synonym_patterns))])
        query += f" OR ({synonym_conditions})"
    
    params = {'disease_name_pattern': disease_name_pattern}
    for i, pattern in enumerate(synonym_patterns):
        params[f'syn_{i}'] = pattern

    return query, params

def execute_query(query, params):
    conn = cx_Oracle.connect(user="ayush", password="aysh7139", dsn=oracle_dsn)
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in results]

if __name__ == '__main__':
    app.run(port=5585, debug=True)
