import pandas as pd

data = { "text": [ 
    "Je te déteste, tu es horrible !",  # Haineux 
    "J'aime beaucoup cette vidéo, merci.",  # Non haineux 
    "Va te faire voir, imbécile.",  # Haineux 
    "Quel contenu inspirant, bravo à l'équipe !",  # Non haineux 
    "Tu es vraiment nul et inutile.",  # Haineux 
    "Je suis impressionné par la qualité de cette vidéo.",  # Non haineux 
    "Ferme-la, personne ne veut entendre ça.",  # Haineux 
    "C'est une discussion constructive, merci pour vos efforts.",  # Non haineux 
    "Ce commentaire est complètement stupide et inutile.",  # Haineux 
    "Merci pour cette vidéo, elle m'a beaucoup aidé !",  # Non haineux 
    "Personne n'a besoin de voir des bêtises pareilles.",  # Haineux 
    "Excellent contenu, continuez comme ça !",  # Non haineux 
    "Tu ne comprends rien, arrête de commenter.",  # Haineux
    "Bravo, c'est exactement ce que je cherchais.",  # Non haineux 
    "Espèce d'idiot, tu ne sais même pas de quoi tu parles.",  # Haineux 
    "Cette vidéo est très claire, merci pour le travail.",  # Non haineux 
    "Tu es une honte, personne ne veut lire ça.",  # Haineux 
    "Le tutoriel est super bien expliqué, merci !",  # Non haineux 
    "C'est complètement débile, arrête de poster.",  # Haineux 
    "J'adore cette chaîne, toujours des vidéos intéressantes.",  # Non haineux 
    "Dégage d'ici, personne ne te supporte.",  # Haineux 
    "Merci pour ces conseils, c'est vraiment utile.",  # Non haineux 
    "T'es vraiment le pire, tes vidéos sont nulles.",  # Haineux 
    "Une très bonne vidéo, claire et précise, bravo !",  # Non haineux 
], 
    "label": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0] 
}
df = pd.DataFrame(data) 
print(df)

import re 
from sklearn.feature_extraction.text import CountVectorizer # Fonction de nettoyage 

def clean_text(text): 
    text = text.lower()  # Mettre en minuscule 
    text = re.sub(r'[^\w\s]', '', text)  # Supprimer les caractères spéciaux 
    return text 
    
# Appliquer le nettoyage 
df['text_clean'] = df['text'].apply(clean_text) 
french_stopwords = [ "le", "la", "les", "un", "une", "des", "du", "de", "dans", "et", "en", "au", "aux", "avec", "ce", "ces", "pour", "par", "sur", "pas", "plus", "où", "mais", "ou", "donc", "ni", "car", "ne", "que", "qui", "quoi", "quand", "à", "son", "sa", "ses", "ils", "elles", "nous", "vous", "est", "sont", "cette", "cet", "aussi", "être", "avoir", "faire", "comme", "tout", "bien", "mal", "on", "lui" ] # Vectorisation (bag of words) 
vectorizer = CountVectorizer(stop_words=french_stopwords, max_features=100) 
X = vectorizer.fit_transform(df['text_clean']) 
y = df['label'] 
print("Vectorisation terminée.")

from sklearn.model_selection import train_test_split
from sklearn. linear_model import LogisticRegression

# Division des données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Entraînement du modèle
model = LogisticRegression()
model. fit(X_train, y_train)
print("Modèle entraîné avec succès.")

from sklearn.metrics import classification_report, confusion_matrix # Prédictions 
y_pred = model.predict(X_test) # Rapport de classification 
print("Rapport de classification :") 
print(classification_report(y_test, y_pred)) # Matrice de confusion 
print("Matrice de confusion :") 
print(confusion_matrix(y_test, y_pred))

# Nouvelles données 
new_comments = [ "Je ne supporte pas cette personne.",  # Haineux 
"Cette vidéo est incroyable, merci pour votre travail.",  # Non haineux 
"Arrête de dire n'importe quoi, imbécile.",  # Haineux 
"Une excellente présentation, bravo à toute l'équipe."  # Non haineux 
] 
# Nettoyage et vectorisation 
new_comments_clean = [clean_text(comment) for comment in new_comments] 
new_comments_vectorized = vectorizer.transform(new_comments_clean)

# Prédictions 
predictions = model.predict(new_comments_vectorized) 
for comment, label in zip(new_comments, predictions): 
    print(f"Commentaire : '{comment}' -> {'Haineux' if label == 1 else 'Non haineux'}")