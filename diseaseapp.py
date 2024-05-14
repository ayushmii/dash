from flask import Flask, jsonify, request,make_response
import os
import psycopg2
import requests
from flask_cors import CORS
app = Flask(__name__)
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
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
@app.route('/latest_records_processing', methods=['GET'])
def get_latest_records_processing():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = (SELECT MAX(info_id) FROM patient_counts_info) AND Status!='Completed';")
        records = cur.fetchall()
        cur.close()
        return jsonify(records)
    except Exception as e:
        print(e)
@app.route('/latest_records_completed', methods=['GET'])
def get_latest_records_completed():
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = (SELECT MAX(info_id) FROM patient_counts_info) AND Status = 'Completed';")
        records = cur.fetchall()
        cur.close()
        return jsonify(records)
    except Exception as e:
        print(e)


@app.route('/infoid_records', methods=['GET'])
def get_infoid_records():
    try:
        cur = conn.cursor()
        info_id = request.args.get('info_id')  # Retrieve info_id from query parameter
        if info_id:
            cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = %s;", (info_id,))
            records = cur.fetchall()
        else:
            records = []
        cur.close()
        return jsonify(records)
    except Exception as e:
        print(e)
# Endpoint to handle the disease count process
# Route to add a new record to the patient_counts_info table
@app.route('/patient_counts_info', methods=['POST'])
def add_patient_counts_info():
    try:
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
    except Exception as e:
        print(e) 
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
    cur.execute("INSERT INTO patient_counts_disease (info_id, sr_no, disease_desc, disease, visits, patients, discharge_summaries, ds_patients, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING info_id,sr_no;", (info_id, sr_no, disease_desc, disease, visits, patients, discharge_summaries, ds_patients, status))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    return jsonify({'info_id': info_id,'sr_no': sr_no})
@app.route('/patient_counts_disease/<int:id>', methods=['PUT'])

def update_patient_counts_disease(id):
    data = request.get_json()
    print(request)
    print("SDDDDDDDDDDDDDDDDDDDDDDD")
    print(data)
    visits = data.get('visits')  # Use .get() instead of direct access
    patients = data.get('patients')
    discharge_summaries = data.get('discharge_summaries')
    ds_patients = data.get('ds_patients')
    status = 'Completed'  # Set the status explicitly
    sr_no = data.get('sr_no')
    print(sr_no)
    cur = conn.cursor()
    cur.execute("""
        UPDATE patient_counts_disease
        SET visits = %s,
            patients = %s,
            discharge_summaries = %s,
            ds_patients = %s,
            status = %s
        WHERE info_id = %s and sr_no=%s
        RETURNING *;
    """, (visits, patients, discharge_summaries, ds_patients, status, id,sr_no))
    print("Query exectued Successfully")
    
    updated_record = cur.fetchone()
    conn.commit()
    cur.close()
    if updated_record:
        response=jsonify({
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
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    else:
        return jsonify({'message': 'No record found with the given ID'}), 404

if __name__ == '__main__':
    port = int(os.getenv('DISEASE_APP_PORT', 5354))  # Use 5353 as default if the env variable is not set
    app.run(port=port, debug=True)