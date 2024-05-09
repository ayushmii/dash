from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# PostgreSQL connection details
HOST = "localhost"
DATABASE = "pgi_data"
USER = "ayush"
PASSWORD = "aysh7139"

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST
        )
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database.")
        print(e)
        return None

@app.route('/api/patient_counts', methods=['GET'])
def get_patient_counts():
    try:
        conn = connect_to_db()
        if conn is None:
            return jsonify("Unable to connect to the database."), 500

        cur = conn.cursor()

        # Extract query parameters
        departments = request.args.get('department')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Convert departments to a list if it's a comma-separated string
        if departments:
            departments = departments.split(',')

        print("Departments:", departments)
        print("Start Date:", start_date)
        print("End Date:", end_date)

        # Construct SQL query based on parameters

        

        query = """
            SELECT * FROM public.m_patient_counts
            WHERE (dept IN %s OR %s IS NULL)
            AND (data_date BETWEEN %s AND %s OR %s IS NULL)
        """

        print("Query:", query)

        # Execute query with proper parameters
        cur.execute(query, (tuple(departments), departments is not None, f"'{start_date}'", f"'{end_date}'", start_date is not None))

        # Fetch all records
        records = cur.fetchall()

        print("Number of records fetched:", len(records))

        # Convert records to JSON
        results = []
        for record in records:
            results.append({
                "col1": record[0],
                "dept": record[1],
                "data_date": record[2].isoformat(),
                "pref": record[3],
                "deidpref": record[4]
            })

        conn.close()
        return jsonify(results), 200

    except Exception as e:
        print("Error:", e)
        return jsonify(str(e)), 500
    
@app.route('/api/departments', methods=['GET'])
def get_departments():
    try:
        conn = connect_to_db()
        if conn is None:
            return jsonify("Unable to connect to the database."), 500

        cur = conn.cursor()
        cur.execute("SELECT department_id, department_name FROM HISDEPARTMENT")
        rows = cur.fetchall()
        departments = [{'id': row[0], 'name': row[1]} for row in rows]
        return jsonify(departments)
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return jsonify({'error': 'Error fetching data from PostgreSQL table'}), 500
    finally:
        if conn:
            cur.close()

if __name__ == '__main__':
    app.run(debug=True)
