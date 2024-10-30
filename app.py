import os
import pymysql
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
CORS(app, origins="http://localhost:3000", methods=["GET", "POST"])

SWAGGER_URL = '/docs'
API_URL = '/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "User API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/openapi.yaml')
def serve_openapi_spec():
    return send_from_directory(os.getcwd(), 'openapi.yaml')

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))  # Default port is 3306 if not provided
}

def fetch_from_db(query, params=None):
    """
    Connects to the database, executes the given query, and returns the result.
    
    Parameters:
    query (str): The SQL query to execute.
    params (tuple): Parameters to pass into the query (optional).
    
    Returns:
    list: The results of the query execution.
    """
    conn = None
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(query, params)

        results = cursor.fetchall()

        return results

    except pymysql.MySQLError as err:
        return f"Error: {err}"

    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/search_user', methods=['GET'])
def search_user():
    username = request.args.get('username')
    
    if not username:
        return jsonify({"error": "username parameter is required"}), 400

    query = "SELECT * FROM Users WHERE username LIKE %s"
    params = (f"%{username}%",)

    results = fetch_from_db(query, params)

    if isinstance(results, str):
        return jsonify({"error": results}), 500

    result_list = []
    for row in results:
        result_list.append({
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "first_name": row[3],
            "last_name": row[4],
            "phone_number": row[5],
            "address": row[6],
            "created_at": row[7].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({"users": result_list}), 200

@app.route('/search_user_by_id', methods=['GET'])
def search_user_by_id():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400

    query = f"SELECT * FROM Users WHERE user_id = {user_id}"
    params = (f"%{user_id}%",)

    # results = fetch_from_db(query, params)
    results = fetch_from_db(query)

    if isinstance(results, str):
        return jsonify({"error": results}), 500

    result_list = []
    for row in results:
        result_list.append({
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "first_name": row[3],
            "last_name": row[4],
            "phone_number": row[5],
            "address": row[6],
            "created_at": row[7].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({"users": result_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8889, debug=True)
