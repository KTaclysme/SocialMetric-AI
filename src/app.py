import json
from flask import Flask, jsonify, request
from src.db.mysql import *
from src.ml.sentiment_model import SentimentAnalyzer

app = Flask(__name__) 
# Créer une instance globale de l'analyseur de sentiment
sentiment_analyzer = SentimentAnalyzer()
# Variable pour suivre si le modèle est entraîné
model_trained = False

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

@app.route('/sentiment/train', methods=['POST'])
def train_model():
    """
    Entraîne le modèle d'analyse de sentiment sur les données de la base de données
    """
    global model_trained
    
    # Récupérer les données depuis la base de données
    cnx = get_mysql_connection()
    if cnx is None:
        return jsonify({'error': 'Unable to connect to the database'}), 500

    cur = cnx.cursor(dictionary=True)
    cur.execute('''SELECT * FROM tweets''')
    data = cur.fetchall()
    cur.close()
    cnx.close()
    
    if not data:
        return jsonify({'error': 'No data available for training'}), 400
    
    try:
        # Charger les données pour l'entraînement
        texts, labels = sentiment_analyzer.load_data(db_data=data)
        
        # Entraîner le modèle
        results = sentiment_analyzer.train(texts, labels)
        
        # Mettre à jour le statut du modèle
        model_trained = True
        
        # Renvoyer les métriques d'évaluation
        metrics = {
            'accuracy': results['accuracy'],
            'classification_report': {
                label: {
                    metric: results['classification_report'][label][metric]
                    for metric in ['precision', 'recall', 'f1-score']
                }
                for label in ['négatif', 'positif']
            },
            'confusion_matrix': results['confusion_matrix'],
            'examples': [
                {
                    'text': results['X_test'][i],
                    'true_sentiment': 'positive' if results['y_test'][i] == 1 else 'negative',
                    'predicted_sentiment': 'positive' if results['y_pred'][i] == 1 else 'negative'
                }
                for i in range(min(5, results['test_size']))
            ]
        }
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': f'Error during model training: {str(e)}'}), 500

@app.route('/sentiment/predict', methods=['POST'])
def predict_sentiment():
    """
    Analyse le sentiment d'un texte fourni en entrée
    """
    global model_trained
    
    # Vérifier si le modèle est entraîné
    if not model_trained:
        return jsonify({'error': 'Model not trained yet. Call /sentiment/train first'}), 400
    
    # Récupérer le texte à analyser
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text parameter'}), 400
    
    text = data['text']
    
    # Effectuer la prédiction
    try:
        predictions = sentiment_analyzer.predict([text])
        return jsonify(predictions[0])
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/sentiment/bulk-predict', methods=['POST'])
def bulk_predict():
    """
    Analyse le sentiment pour plusieurs textes en une seule requête
    """
    global model_trained
    
    # Vérifier si le modèle est entraîné
    if not model_trained:
        return jsonify({'error': 'Model not trained yet. Call /sentiment/train first'}), 400
    
    # Récupérer les textes à analyser
    data = request.get_json()
    
    if not data or 'texts' not in data or not isinstance(data['texts'], list):
        return jsonify({'error': 'Missing or invalid texts parameter'}), 400
    
    texts = data['texts']
    
    # Effectuer les prédictions
    try:
        predictions = sentiment_analyzer.predict(texts)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/sentiment/train-url', methods=['GET'])
def train_model_url():
    """
    Entraîne le modèle d'analyse de sentiment en utilisant les paramètres fournis dans l'URL
    Exemple d'URL: /sentiment/train-url?text=Ce+produit+est+excellent&sentiment=positive
    """
    global model_trained
    
    # Récupérer les paramètres de l'URL
    text = request.args.get('text')
    sentiment = request.args.get('sentiment')
    
    if not text or not sentiment:
        return jsonify({'error': 'Les paramètres text et sentiment sont requis'}), 400
    
    # Valider le sentiment
    if sentiment.lower() not in ['positive', 'negative']:
        return jsonify({'error': 'Le sentiment doit être "positive" ou "negative"'}), 400
    
    # Convertir en format numérique (1 pour positif, 0 pour négatif)
    label = 1 if sentiment.lower() == 'positive' else 0
    
    try:
        # Ajouter l'exemple à la base de données
        cnx = get_mysql_connection()
        if cnx is None:
            return jsonify({'error': 'Unable to connect to the database'}), 500

        cur = cnx.cursor()
        cur.execute('''INSERT INTO tweets (text, positive, negative) VALUES (%s, %s, %s)''', 
                    (text, 1 if label == 1 else 0, 1 if label == 0 else 0))
        cnx.commit()
        cur.close()
        cnx.close()
        
        # Récupérer toutes les données pour réentraîner le modèle
        cnx = get_mysql_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute('''SELECT * FROM tweets''')
        data = cur.fetchall()
        cur.close()
        cnx.close()
        
        if not data:
            return jsonify({'error': 'No data available for training'}), 400
        
        # Charger les données pour l'entraînement
        texts, labels = sentiment_analyzer.load_data(db_data=data)
        
        # Entraîner le modèle
        results = sentiment_analyzer.train(texts, labels)
        
        # Mettre à jour le statut du modèle
        model_trained = True
        
        return jsonify({
            'success': True,
            'message': 'Exemple ajouté et modèle réentraîné avec succès',
            'added_example': {
                'text': text,
                'sentiment': sentiment
            },
            'total_examples': len(texts),
            'accuracy': results['accuracy']
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'entraînement: {str(e)}'}), 500

@app.route('/sentiment/train-batch-url', methods=['GET'])
def train_model_batch_url():
    """
    Entraîne le modèle d'analyse de sentiment avec plusieurs exemples fournis dans l'URL
    Exemple d'URL: /sentiment/train-batch-url?data={"texts":["Produit génial!","Service horrible"],"sentiments":["positive","negative"]}
    """
    global model_trained
    
    # Récupérer les paramètres de l'URL
    data_json = request.args.get('data')
    
    if not data_json:
        return jsonify({'error': 'Le paramètre data est requis avec le format JSON'}), 400
    
    try:
        # Convertir la chaîne JSON en objet Python
        data = json.loads(data_json)
        
        if 'texts' not in data or 'sentiments' not in data:
            return jsonify({'error': 'Le JSON doit contenir les clés "texts" et "sentiments"'}), 400
            
        texts = data.get('texts', [])
        sentiments = data.get('sentiments', [])
        
        if len(texts) != len(sentiments):
            return jsonify({'error': 'Le nombre de textes doit être égal au nombre de sentiments'}), 400
            
        if len(texts) == 0:
            return jsonify({'error': 'Au moins un exemple est requis'}), 400
        
        # Valider les sentiments
        for sentiment in sentiments:
            if sentiment.lower() not in ['positive', 'negative']:
                return jsonify({'error': f'Le sentiment "{sentiment}" doit être "positive" ou "negative"'}), 400
        
        # Ajouter les exemples à la base de données
        cnx = get_mysql_connection()
        if cnx is None:
            return jsonify({'error': 'Unable to connect to the database'}), 500

        cur = cnx.cursor()
        
        for i, text in enumerate(texts):
            sentiment = sentiments[i].lower()
            positive = 1 if sentiment == 'positive' else 0
            negative = 1 if sentiment == 'negative' else 0
            
            cur.execute('''INSERT INTO tweets (text, positive, negative) VALUES (%s, %s, %s)''', 
                       (text, positive, negative))
                       
        cnx.commit()
        cur.close()
        cnx.close()
        
        # Récupérer toutes les données pour réentraîner le modèle
        cnx = get_mysql_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute('''SELECT * FROM tweets''')
        data = cur.fetchall()
        cur.close()
        cnx.close()
        
        if not data:
            return jsonify({'error': 'No data available for training'}), 400
        
        # Charger les données pour l'entraînement
        all_texts, all_labels = sentiment_analyzer.load_data(db_data=data)
        
        # Entraîner le modèle
        results = sentiment_analyzer.train(all_texts, all_labels)
        
        # Mettre à jour le statut du modèle
        model_trained = True
        
        return jsonify({
            'success': True,
            'message': f'{len(texts)} exemples ajoutés et modèle réentraîné avec succès',
            'added_examples': [
                {'text': texts[i], 'sentiment': sentiments[i]} 
                for i in range(len(texts))
            ],
            'total_examples': len(all_texts),
            'accuracy': results['accuracy']
        })
        
    except json.JSONDecodeError:
        return jsonify({'error': 'Format JSON invalide'}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'entraînement: {str(e)}'}), 500

@app.route('/sentiment/predict-url', methods=['GET'])
def predict_sentiment_url():
    """
    Analyse le sentiment d'un texte fourni en paramètre d'URL
    Exemple d'URL: /sentiment/predict-url?text=Ce+produit+est+excellent
    """
    global model_trained
    
    # Vérifier si le modèle est entraîné
    if not model_trained:
        return jsonify({'error': 'Le modèle n\'est pas encore entraîné. Appelez /sentiment/train d\'abord'}), 400
    
    # Récupérer le texte à analyser
    text = request.args.get('text')
    
    if not text:
        return jsonify({'error': 'Le paramètre text est requis'}), 400
    
    # Effectuer la prédiction
    try:
        predictions = sentiment_analyzer.predict([text])
        return jsonify(predictions[0])
    except Exception as e:
        return jsonify({'error': f'Erreur de prédiction: {str(e)}'}), 500