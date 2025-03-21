from joblib import load
import emoji
import re

def clean_tweet(text):
    """Nettoie le texte du tweet"""
    text = emoji.replace_emoji(text, '')
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_sentiment(text):
    # Charger le modèle et le vectorizer
    model = load('models/sentiment_model.joblib')
    vectorizer = load('models/vectorizer.joblib')
    
    # Nettoyer et vectoriser le texte
    cleaned_text = clean_tweet(text)
    text_vectorized = vectorizer.transform([cleaned_text])
    
    # Faire la prédiction
    prediction = model.predict(text_vectorized)[0]
    proba = model.predict_proba(text_vectorized)[0]
    
    # Convertir la prédiction en score entre -1 et 1
    score = (proba[1] - 0.5) * 2  # Convertit [0,1] en [-1,1]
    
    return {
        'text': text,
        'cleaned_text': cleaned_text,
        'score': float(score),
        'probability': float(proba[1])
    }

if __name__ == "__main__":
    # Exemples de test
    test_tweets = [
        "This product is amazing!",
        "Terrible service, would not recommend",
        "Pretty good experience overall",
        "I love this, it's perfect!",
        "Worst purchase ever, total garbage"
    ]
    
    print("\nTest de prédiction de sentiments :")
    print("-" * 50)
    
    for tweet in test_tweets:
        result = predict_sentiment(tweet)
        print(f"\nTexte original : {result['text']}")
        print(f"Texte nettoyé  : {result['cleaned_text']}")
        print(f"Score          : {result['score']:.2f}")
        print(f"Probabilité    : {result['probability']:.2%}")
        print("-" * 50) 