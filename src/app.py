from flask import Flask, jsonify, request
from src.db.mysql import *

app = Flask(__name__) 

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