import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import json
import os
from src.ml.stopwords_fr import STOPWORDS_FR

class SentimentAnalyzer:
    def __init__(self):
        # Initialiser le vectoriseur avec les stop words
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words=STOPWORDS_FR)
        self.model = LogisticRegression(max_iter=1000, C=1.0, solver='liblinear')
        self.is_trained = False
        
    def load_data(self, json_file=None, db_data=None):
        """
        Charge les données depuis un fichier JSON ou à partir des données extraites de la DB
        """
        if json_file and os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif db_data:
            data = db_data
        else:
            raise ValueError("Aucune source de données valide fournie")
            
        texts = [item['text'] for item in data]
        labels = [1 if item['positive'] == 1 else 0 for item in data]  # 1 pour positif, 0 pour négatif
        
        return texts, labels
    
    def train(self, texts, labels, test_size=0.2, random_state=42):
        """
        Entraîne le modèle de régression logistique sur les données
        """
        # Diviser les données en ensembles d'entraînement et de test
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=random_state
        )
        
        # Vectorisation des textes
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Entraînement du modèle
        self.model.fit(X_train_vec, y_train)
        self.is_trained = True
        
        # Évaluation du modèle
        y_pred = self.model.predict(X_test_vec)
        
        # Résultats d'évaluation
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, target_names=['négatif', 'positif'], output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'test_size': len(y_test),
            'X_test': X_test,  # Conserver les textes de test pour l'affichage
            'y_test': y_test,  # Conserver les vraies étiquettes pour l'affichage
            'y_pred': y_pred.tolist(),  # Conserver les prédictions pour l'affichage
            'stopwords_enabled': True  # Indiquer si les stop words sont utilisés
        }
        
        return results
    
    def predict(self, texts):
        """
        Prédit le sentiment de nouveaux textes
        """
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
            
        # Vectoriser les textes
        X_vec = self.vectorizer.transform(texts)
        
        # Prédire les sentiments
        probas = self.model.predict_proba(X_vec)
        predictions = self.model.predict(X_vec)
        
        # Formater les résultats
        results = []
        for i, text in enumerate(texts):
            label = "positive" if predictions[i] == 1 else "negative"
            confidence = probas[i][1] if predictions[i] == 1 else probas[i][0]
            results.append({
                'text': text,
                'sentiment': label,
                'confidence': float(confidence)
            })
            
        return results 