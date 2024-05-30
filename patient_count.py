from flask import Flask, request, jsonify
import os
import psycopg2
import requests
from flask import Blueprint, jsonify
from flask_cors import CORS
from dotenv import dotenv_values
env_vars = dotenv_values('.env')  
app = Flask(__name__)

CORS(app)
# Database connection
conn = psycopg2.connect(
   host="localhost",
    database="pgi_data",
    user=env_vars.get('POSTGRES_USER', 'ayush'),
    password=env_vars.get('POSTGRES_PASSWORD', 'aysh7139')
)
cur = conn.cursor()

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
    user=env_vars.get('POSTGRES_USER', 'ayush'),
    password=env_vars.get('POSTGRES_PASSWORD', 'aysh7139')
    )
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return [dict((cursor.description[i][0], value) \
                 for i, value in enumerate(row)) for row in results]

if __name__ == '__main__':
    port = int(env_vars.get('PATIENT_COUNT_PORT', 7657))
    app.run(port=port, debug=True)