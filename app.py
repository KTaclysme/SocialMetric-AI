import os
import time
import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)

def create_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "user"),
        password=os.getenv("MYSQL_PASSWORD", "password"),
        database=os.getenv("MYSQL_DB", "mydb")
    )

def get_mysql_connection():
    try:
        cnx = create_connection()
        if cnx.is_connected():
            print("Connexion réussie à MySQL !")
            return cnx
    except mysql.connector.Error as err:
        print(f"Impossible de se connecter à MySQL : {err}")
        return None

def create_table():
    cnx = get_mysql_connection()
    if cnx is None:
        return jsonify({'error': 'Unable to connect to the database'}), 500
    
    cur = cnx.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS tweets (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        text VARCHAR(255), 
        positive INT DEFAULT 0, 
        negative INT DEFAULT 0)''')
    cnx.commit()
    cur.close()
    cnx.close()
    return jsonify({'message': 'Table created successfully'})

@app.route('/')
def hello():
    return '<p>Hello World! <br> <a href="http://localhost:5000/data">click here</a> to create a table and show data </p>'

@app.route('/data', methods=['GET'])
def get_data():
    cnx = get_mysql_connection()
    create_table()
    if cnx is None:
        return jsonify({'error': 'Unable to connect to the database'}), 500

    cur = cnx.cursor(dictionary=True)
    cur.execute('''SELECT * FROM tweets''')
    data = cur.fetchall()
    cur.close()
    cnx.close()
    return jsonify(data)


@app.route('/data', methods=['POST'])
def add_data():
    text = request.json['text']
    
    cnx = get_mysql_connection()
    if cnx is None:
        return jsonify({'error': 'Unable to connect to the database'}), 500
    
    cur = cnx.cursor()
    cur.execute('''INSERT INTO tweets (text) VALUES (%s)''', (text,))
    cnx.commit()
    cur.close()
    cnx.close()
    return jsonify({'message': 'Data added successfully'})

if __name__ == '__main__':
    while True:
        cnx = get_mysql_connection()
        if cnx:
            break
        else:
            print("Nouvelle tentative dans 5 secondes...")
            time.sleep(5)
    
    app.run(debug=True, host='0.0.0.0')
