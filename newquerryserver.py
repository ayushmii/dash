from flask import Flask, request, jsonify
import os
import psycopg2
import requests
from flask import Blueprint, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
CORS(app)
# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="pgi_data",
    user="ayush",
    password="aysh7139"
)
cur = conn.cursor()

@app.route('/patient_counts', methods=['GET'])
def get_patient_counts():
    # Get parameters from the request
    dept_names = request.args.get('dept_names', '').split(',')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    grouping = request.args.get('grouping', 'monthly')  # Default to monthly

    # Prepare the SQL query
    # Prepare the SQL query
    query = """
        SELECT col1, dept, 
            DATE_TRUNC(%s, data_date) AS data_date,
            MIN(data_date) AS data_from,
            MAX(data_date) AS data_upto,
            COUNT(*) AS rec_count,
            COUNT(DISTINCT deidpref) AS patient_count,
            (SELECT d.department_name FROM HISDEPARTMENT d WHERE d.department_id = M_PATIENT_COUNTS.dept) AS dept_name
        FROM M_PATIENT_COUNTS
        WHERE data_date BETWEEN %s AND %s
            AND (SELECT d.department_name FROM HISDEPARTMENT d WHERE d.department_id = M_PATIENT_COUNTS.dept) IN %s
        GROUP BY col1, dept, DATE_TRUNC(%s, data_date)
        ORDER BY dept, col1;
    """

    # Prepare the grouping function and clause based on the grouping parameter
    if grouping == 'monthly':
        grouping_func = 'month'
    elif grouping == 'yearly':
        grouping_func = 'year'
    elif grouping == 'weekly':
        grouping_func = 'week'
    else:
        return jsonify({'error': 'Invalid grouping parameter'}), 400

    # Execute the query
    cur.execute(query, (grouping_func, start_date, end_date, tuple(dept_names), grouping_func))


    # Execute the query
    
    rows = cur.fetchall()

    # Convert the result to a list of dictionaries
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

@app.route('/departments', methods=['GET'])
def get_department_names():
    try:
        # Execute the SQL query to retrieve department names
        cur.execute("SELECT department_name FROM HISDEPARTMENT")

        # Fetch all rows
        rows = cur.fetchall()

        # Extract department names from the result
        department_names = [row[0] for row in rows]

        # Return department names as JSON response
        return jsonify(department_names)

    except psycopg2.Error as e:
        # Handle database errors
        error_message = "Database error: {}".format(e)
        return jsonify({"error": error_message}), 500

    except Exception as e:
        # Handle other exceptions
        error_message = "Error: {}".format(e)
        return jsonify({"error": error_message}), 500


@app.route('/disease_counts', methods=['GET'])
def get_disease_counts():
    disease_name = request.args.get('disease_name')
    date_from=request.args.get('date_from')
    date_to=request.args.get('date_to')
    print(disease_name)
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
                    print(result['name'])
                    synonyms.append(result['name'])
        return synonyms
    else:
        print(f"Failed to fetch synonyms for '{disease_name}': {response.status_code} - {response.text}")
        return []
    
#The Count credentials for this database will be different.
#Two option: Postgres or Oracle
#Make Connection options dynamic

def construct_query(disease_name, synonyms):
    # Prepare the disease name and synonyms for use in the query
    disease_name_pattern = f"%{disease_name.lower().replace(' ', '')}%"
    synonym_patterns = [f"%{syn.lower().replace(' ', '')}%" for syn in synonyms]

    # Construct the query with dynamic parameters
    query = """
            SELECT  count(*) AS visits,23 as patients,9 as discharge_summaries ,4 as ds_patients 
            FROM disease_record
            WHERE
                LOWER(REPLACE(disease_name, ' ', '')) LIKE %s
                OR LOWER(REPLACE(disease_desc, ' ', '')) LIKE %s
            
        """

    # Add additional condition for synonyms
    if synonym_patterns:
        synonym_conditions = " OR ".join([f"LOWER(REPLACE(disease_desc, ' ', '')) LIKE %s" for _ in synonym_patterns])
        query += f"    OR ({synonym_conditions})"
    
    params = [disease_name_pattern, disease_name_pattern] + synonym_patterns
    
    return query, params

def execute_query(query, params):
    conn = psycopg2.connect(
        host="localhost",
        database="pgi_data",
        user="ayush",
        password="aysh7139"
    )
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [dict((cursor.description[i][0], value) \
                 for i, value in enumerate(row)) for row in results]

if __name__ == '__main__':
    app.run(port=5555, debug=True)