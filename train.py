import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import re
import emoji
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump
import os

def clean_tweet(text):
    """Nettoie le texte du tweet"""
    # Supprime les emojis
    text = emoji.replace_emoji(text, '')
    # Convertit en minuscules
    text = text.lower()
    # Supprime les URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Supprime les mentions @utilisateur
    text = re.sub(r'@\w+', '', text)
    # Supprime les hashtags
    text = re.sub(r'#\w+', '', text)
    # Supprime les caractères spéciaux et chiffres
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # Supprime les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def train_model():
    # Connexion à la base de données
    DATABASE_URL = "mysql+pymysql://user:password@db/mydb"
    engine = create_engine(DATABASE_URL)
    
    # Chargement des données
    query = "SELECT text, positive, negative FROM tweets"
    df = pd.read_sql(query, engine)
    
    # Vérification des données
    print(f"Nombre de tweets récupérés : {len(df)}")
    if len(df) == 0:
        print("Aucun tweet trouvé dans la base de données!")
        print("Vérifiez que :")
        print("1. La table 'tweets' existe")
        print("2. La table contient des données")
        print("3. Les colonnes 'text', 'positive', 'negative' existent")
        return
        
    # Afficher les premières lignes pour vérification
    print("\nAperçu des données :")
    print(df.head())
    
    # Nettoyage des tweets
    df['cleaned_text'] = df['text'].apply(clean_tweet)
    
    # Création des labels (1 pour positif, 0 pour négatif)
    df['label'] = df['positive'].astype(int)
    
    # Séparation des données
    X = df['cleaned_text']
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Vectorisation du texte
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    # Entraînement du modèle
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vectorized, y_train)
    
    # Évaluation du modèle
    y_pred = model.predict(X_test_vectorized)
    print("\nRapport de classification :")
    print(classification_report(y_test, y_pred))
    
    # Création du dossier models s'il n'existe pas
    os.makedirs('models', exist_ok=True)
    
    # Sauvegarde du modèle et du vectorizer
    dump(model, 'models/sentiment_model.joblib')
    dump(vectorizer, 'models/vectorizer.joblib')
    
    print("\nModèle et vectorizer sauvegardés dans le dossier 'models'")

if __name__ == "__main__":
    train_model() 