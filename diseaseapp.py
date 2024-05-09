from flask import Flask, jsonify, request
import os
import psycopg2
import requests
from flask_cors import CORS
app = Flask(__name__)
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


CORS(app)
# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="pgi_data",
    user="ayush",
    password="aysh7139"
)

# CORS setup
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Endpoint to fetch the latest records from 'patient_counts_disease' table
@app.route('/latest_records', methods=['GET'])
def get_latest_records():
    cur = conn.cursor()
    cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = (SELECT MAX(info_id) FROM patient_counts_info);")
    records = cur.fetchall()
    cur.close()
    return jsonify(records)


# Endpoint to handle the disease count process
# Route to add a new record to the patient_counts_info table
@app.route('/patient_counts_info', methods=['POST'])
def add_patient_counts_info():
    data = request.get_json()
    short_desc = data['short_desc']
    data_from = data['data_from']
    data_upto = data['data_upto']
    status = data['status']

    cur = conn.cursor()
    cur.execute("INSERT INTO patient_counts_info (short_desc, data_from, data_upto, status, process_date) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING info_id;", (short_desc, data_from, data_upto, status))
    new_info_id = cur.fetchone()[0]
        
    conn.commit()
    cur.close()

    return jsonify({'info_id': new_info_id})

# Route to add a new record to the patient_counts_disease table
@app.route('/patient_counts_disease', methods=['POST'])
def add_patient_counts_disease():
    data = request.get_json()
    info_id = data['info_id']
    sr_no = data['sr_no']
    disease_desc = data['disease_desc']
    disease = data['disease']
    visits = data['visits']
    patients = data['patients']
    discharge_summaries = data['discharge_summaries']
    ds_patients = data['ds_patients']
    status = data['status']

    cur = conn.cursor()
    cur.execute("INSERT INTO patient_counts_disease (info_id, sr_no, disease_desc, disease, visits, patients, discharge_summaries, ds_patients, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", (info_id, sr_no, disease_desc, disease, visits, patients, discharge_summaries, ds_patients, status))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    return jsonify({'id': new_id})

@app.route('/patient_counts_disease/<int:id>', methods=['PUT'])
def update_patient_counts_disease(id):
    data = request.get_json()
    visits = data['visits']
    patients = data['patients']
    discharge_summaries = data['discharge_summaries']
    ds_patients = data['ds_patients']
    status = data['status']

    cur = conn.cursor()
    cur.execute("""
        UPDATE patient_counts_disease
        SET visits = %s,
            patients = %s,
            discharge_summaries = %s,
            ds_patients = %s,
            status = %s
        WHERE info_id = %s
        RETURNING *;
    """, (visits, patients, discharge_summaries, ds_patients, status, id))

    updated_record = cur.fetchone()
    conn.commit()
    cur.close()

    if updated_record:
        return jsonify({
            'id': updated_record[0],
            'info_id': updated_record[1],
            'sr_no': updated_record[2],
            'disease_desc': updated_record[3],
            'disease': updated_record[4],
            'visits': updated_record[5],
            'patients': updated_record[6],
            'discharge_summaries': updated_record[7],
            'ds_patients': updated_record[8],
            'status': updated_record[9]
        })
    else:
        return jsonify({'message': 'No record found with the given ID'}), 404

if __name__ == '__main__':
    port = int(os.getenv('DISEASE_APP_PORT', 5354))  # Use 5353 as default if the env variable is not set
    app.run(port=port, debug=True)