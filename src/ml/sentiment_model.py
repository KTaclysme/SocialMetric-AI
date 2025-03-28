from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import json
import os
from ml.stopwords_fr import STOPWORDS_FR

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
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=random_state
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        self.model.fit(X_train_vec, y_train)
        self.is_trained = True
        
        y_pred = self.model.predict(X_test_vec)
        
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
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
            
        X_vec = self.vectorizer.transform(texts)
        
        # Prédire les sentiments
        probas = self.model.predict_proba(X_vec)
        predictions = self.model.predict(X_vec)
        
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

    def save_model(self, model_path):
        import pickle
        import os
        import datetime

        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'vectorizer': self.vectorizer,
                'training_date': datetime.datetime.now().isoformat()
            }, f)

        return True

    def load_model(self, model_path):
        import pickle

        with open(model_path, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.vectorizer = data['vectorizer']
        self.is_trained = True

        return True

    def predict(self, texts):
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")

        X_vec = self.vectorizer.transform(texts)

        probas = self.model.predict_proba(X_vec)

        results = []
        for i, text in enumerate(texts):
            score = (probas[i][1] * 2) - 1

            sentiment = "positive" if score > 0 else "negative"

            results.append({
                'text': text,
                'sentiment': sentiment,
                'confidence': float(abs(score)),
                'score': float(score)
            })

        return results