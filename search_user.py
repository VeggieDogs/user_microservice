from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

db_config = {
    'host': 'veggie-dogs-db.czrcm8qnf1xc.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'dbuserdbuser',
    'database': 'user',
    'port': 3306
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
        return jsonify({"error": "Username parameter is required"}), 400

    query = "SELECT * FROM User WHERE username LIKE %s"
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

    return jsonify(result_list), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
