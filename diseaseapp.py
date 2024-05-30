from flask import Flask, jsonify, request, make_response
import os
import psycopg2
from flask_cors import CORS
from dotenv import dotenv_values

app = Flask(__name__)
env_vars = dotenv_values('.env')   # take environment variables from .env.

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="pgi_data",
    user=env_vars.get('POSTGRES_USER', 'ayush'),
    password=env_vars.get('POSTGRES_PASSWORD', 'aysh7139')
)

# CORS setup
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def rollback_and_close_cursor(cur):
    try:
        conn.rollback()  # Rollback the transaction
    except psycopg2.Error as rollback_error:
        print("Rollback failed:", rollback_error)
    finally:
        if cur:
            cur.close()  # Close the cursor

@app.route('/latest_records_processing', methods=['GET'])
def get_latest_records_processing():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = (SELECT MAX(info_id) FROM patient_counts_info WHERE status != 'Completed') AND Status!='Completed';")
        records = cur.fetchall()
        return jsonify(records)
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

@app.route('/delete_record', methods=['DELETE'])
def delete_record():
    print(request.get_json())
    info_id = request.json.get('info_id')
    sr_no = request.json.get('sr_no')
    if not info_id or not sr_no:
        return jsonify({'message': 'Missing required parameters'}), 400

    try:
        cursor = conn.cursor()
        # Execute a SQL query to delete the record
        query = "DELETE FROM patient_counts_disease WHERE info_id = %s AND sr_no = %s"
        values = (info_id, sr_no)
        cursor.execute(query, values)

        if cursor.rowcount == 0:
            return jsonify({'message': 'Record not found'}), 404

        # Commit the changes to the database
        conn.commit()

        return jsonify({'message': 'Record deleted successfully'})
    except Exception as e:
        print(f'Error deleting record: {e}')
        return jsonify({'message': 'Internal server error'}), 500
@app.route('/previous_records', methods=['GET'])
def get_previous_records():
    cur = None
    try:
        cur = conn.cursor()
        query = """
            WITH FirstDesc AS (
                SELECT DISTINCT ON (info_id)
                    info_id,
                    disease_desc,
                    TO_CHAR(processed_date, 'DD/MM/YYYY') AS formatted_date
                FROM patient_counts_disease
                ORDER BY info_id, sr_no -- assuming sr_no can be used to determine the first record
            )
            SELECT
                pcd.info_id,
                STRING_AGG(pcd.disease, ', ') AS diseases,
                fd.disease_desc AS disease_description,
                fd.formatted_date AS formatted_date
            FROM patient_counts_disease pcd
            JOIN FirstDesc fd ON pcd.info_id = fd.info_id
            GROUP BY pcd.info_id, fd.disease_desc, fd.formatted_date
            ORDER BY pcd.info_id DESC;
        """
        cur.execute(query)
        records = cur.fetchall()
        print(records)
        return jsonify(records)
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()


@app.route('/latest_records_completed', methods=['GET'])
def get_latest_records_completed():
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = (SELECT MAX(info_id) FROM patient_counts_info WHERE status = 'Completed') AND status = 'Completed';")
        records = cur.fetchall()
        return jsonify(records)
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

@app.route('/info_records', methods=['GET'])
def get_info_records():
    cur = None
    try:
        cur = conn.cursor()
        info_id = request.args.get('info_id')
        if info_id:
            cur.execute("SELECT * FROM patient_counts_info WHERE info_id = %s;", (info_id,))
            records = cur.fetchall()
        else:
            records = []
        return jsonify(records)
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()


@app.route('/infoid_records', methods=['GET'])
def get_infoid_records():
    cur = None
    try:
        cur = conn.cursor()
        info_id = request.args.get('info_id')
        if info_id:
            cur.execute("SELECT * FROM patient_counts_disease WHERE info_id = %s;", (info_id,))
            records = cur.fetchall()
        else:
            records = []
        return jsonify(records)
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

@app.route('/patient_counts_info', methods=['POST'])
def add_patient_counts_info():
    cur = None
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
        return jsonify({'info_id': new_info_id})
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

import requests

@app.route('/patient_counts_disease', methods=['POST'])
def add_patient_counts_disease():
    cur = None
    try:
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
        port = env_vars.get('REACT_APP_DISEASE_APP_PORT')
        dateRangeResponse = requests.get(f'http://localhost:{port}/info_records?info_id={info_id}')
        response_data = dateRangeResponse.json()
        #print(response_data)
# Access the data based on the structure of the JSON response
# For example, if the response is a list of lists:
        data_from = response_data[0][3]
        data_upto = response_data[0][4]
        patient_count_stack_port = env_vars.get('PATIENT_COUNT_STACK_PORT')
        search_response = requests.post(f'http://localhost:{patient_count_stack_port}/process_request', json={'disease_name': disease, 'date_from': data_from, 'date_to': data_upto, 'info_id': info_id, 'sr_no': sr_no})
        #print("SSS")


        return jsonify({'info_id': info_id, 'sr_no': sr_no})
    except Exception as e:
        print(e)
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

@app.route('/max_sr_no', methods=['GET'])
def get_max_sr_no():
    cur = None
    try:
        cur = conn.cursor()
        info_id = request.args.get('info_id')
        if info_id:
            cur.execute("SELECT MAX(sr_no) FROM patient_counts_disease WHERE info_id = %s;", (info_id,))
            records = cur.fetchall()
        else:
            records = []
        return jsonify(records)
    except Exception as e:
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
       

@app.route('/patient_counts_disease/<int:id>', methods=['PUT'])
def update_patient_counts_disease(id):
    cur = None
    try:
        data = request.get_json()
        visits = data.get('visits')
        patients = data.get('patients')
        discharge_summaries = data.get('discharge_summaries')
        ds_patients = data.get('ds_patients')
        status = 'Completed'
        sr_no = data.get('sr_no')
        print(request.get_json())
        cur = conn.cursor()
        cur.execute("""
            UPDATE patient_counts_disease
            SET visits = %s,
                patients = %s,
                discharge_summaries = %s,
                ds_patients = %s,
                status = %s
            WHERE info_id = %s and sr_no = %s
            RETURNING *;
        """, (visits, patients, discharge_summaries, ds_patients, status, id, sr_no))
        updated_record = cur.fetchone()
        cur.execute("""
            UPDATE patient_counts_info
            SET status = %s
            WHERE info_id = %s
            RETURNING *;
        """, (status ,id))
        print("Executed")
        
        print("sds")
        print(updated_record)
        conn.commit()
        if updated_record:
            
            print("COMPLETEDDD!!!!")
            print(f"adadas{updated_record}")
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
    except Exception as e:
        print(e)
        rollback_and_close_cursor(cur)
        return jsonify({'error': str(e)}), 500
    finally:
        if cur:
            cur.close()

if __name__ == '__main__':
    port = int(env_vars.get('REACT_APP_DISEASE_APP_PORT', 5354))
    app.run(port=port, debug=True)
