import threading
import queue
import pickle
import requests
from flask import Flask, request, jsonify
from dotenv import dotenv_values
env_vars = dotenv_values('.env')  
app = Flask(__name__)
request_queue = queue.Queue()
request_file = 'requests.pkl'

# Function to process requests
def process_requests():
    while True:
        try:
            # Get the next request from the queue
            req_data = request_queue.get()

            # Process the request
            process_disease_counts_single(req_data)
            print(request_queue.qsize())
            # Mark the request as processed
            request_queue.task_done()
        except Exception as e:
            # Handle any exceptions that occur during request processing
            print(f"Error processing request: {e}")

# Function to process disease_counts_single requests
def process_disease_counts_single(req_data):
    disease_name = req_data['disease_name']
    date_from = req_data['date_from']
    date_to = req_data['date_to']
    info_id = req_data['info_id']
    sr_no = req_data['sr_no']

    # Call the /disease_counts endpoint
    patient_count_port=env_vars.get('PATIENT_COUNT_PORT')
    response = requests.get(f'http://localhost:{patient_count_port}/disease_counts?disease_name={disease_name}&date_from={date_from}&date_to={date_to}')

    # Process the response as needed
    if response.status_code == 200:
        disease_count = response.json()
        # Prepare the data for the PUT request
        data = {
            'sr_no': sr_no,
            'visits': disease_count[0]['visits'],
            'patients': disease_count[0]['patients'],
            'discharge_summaries': disease_count[0]['discharge_summaries'],
            'ds_patients': disease_count[0]['ds_patients']
        }

        # Send the PUT request to update the patient_counts_disease record
        patient_disease_port=env_vars.get('REACT_APP_DISEASE_APP_PORT')
        update_response = requests.put(f'http://localhost:{patient_disease_port}/patient_counts_disease/{info_id}', json=data)
        if update_response.status_code == 200:
            print("Record updated successfully.")
        else:
            print(f"Error updating record: {update_response.status_code} - {update_response.text}")
    else:
        print(f"Error calling /disease_counts: {response.status_code} - {response.text}")

# Start a new thread for processing requests
processor_thread = threading.Thread(target=process_requests, daemon=True)
processor_thread.start()

@app.route('/process_request', methods=['POST'])
def process_request():
    # Get the request data
    req_data = request.get_json()

    # Add the request data to the queue
    request_queue.put(req_data)
    print(request_queue.qsize())
    # Save the request data to a file
    save_request_to_file(req_data)

    # Return a response indicating that the request was received
    return jsonify({'message': 'Request received and queued for processing.'}), 202

def save_request_to_file(req_data):
    try:
        with open(request_file, 'ab') as f:
            pickle.dump(req_data, f)
    except Exception as e:
        print(f"Error saving request to file: {e}")

if __name__ == '__main__':
    try:
        port = int(env_vars.get('PATIENT_COUNT_STACK_PORT', 7346))
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        print("Stopping server...")
