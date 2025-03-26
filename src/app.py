import json
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
    try:
        with open('data/tweets_data.json', 'r', encoding='utf-8') as file:
            tweets = json.load(file)
    except FileNotFoundError:
        return jsonify({'error': 'Le fichier tweets_data.json est introuvable'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Erreur lors de la lecture du fichier JSON'}), 400

    cnx = get_mysql_connection()
    if cnx is None:
        return jsonify({'error': 'Unable to connect to the database'}), 500

    cur = cnx.cursor()

    for tweet in tweets:
        text = tweet.get('text')
        positive = tweet.get('positive')
        negative = tweet.get('negative')

        cur.execute('''INSERT INTO tweets (text, positive, negative) VALUES (%s, %s, %s)''', (text, positive, negative))

    cnx.commit()
    cur.close()
    cnx.close()

    return jsonify({'message': 'Data added successfully'})