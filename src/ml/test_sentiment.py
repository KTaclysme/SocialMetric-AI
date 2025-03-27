import os
import sys
import json

# Ajouter le répertoire parent au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.sentiment_model import SentimentAnalyzer
from db.mysql import get_mysql_connection

def main():
    print("=== Test du modèle d'analyse de sentiment ===")
    
    # Créer l'analyseur de sentiment
    analyzer = SentimentAnalyzer()
    
    # 1. Chargement des données depuis le fichier JSON
    json_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/tweets_data.json"))
    print(f"Chargement des données depuis {json_file}")
    
    try:
        texts, labels = analyzer.load_data(json_file=json_file)
        print(f"Données chargées avec succès: {len(texts)} tweets")
    except Exception as e:
        print(f"Erreur lors du chargement des données: {str(e)}")
        return
    
    # 2. Entraînement et évaluation du modèle
    print("\nEntraînement du modèle de régression logistique...")
    results = analyzer.train(texts, labels, test_size=0.3)
    
    # 3. Affichage des performances
    print("\n=== Résultats de l'évaluation ===")
    print(f"Précision (accuracy): {results['accuracy']:.4f}")
    
    print("\nRapport de classification:")
    report = results['classification_report']
    for label in ['négatif', 'positif']:
        print(f"  {label}:")
        print(f"    Précision: {report[label]['precision']:.4f}")
        print(f"    Rappel: {report[label]['recall']:.4f}")
        print(f"    F1-score: {report[label]['f1-score']:.4f}")
    
    print(f"\nMatrice de confusion:")
    conf_matrix = results['confusion_matrix']
    print(f"  [[{conf_matrix[0][0]}, {conf_matrix[0][1]}]")
    print(f"   [{conf_matrix[1][0]}, {conf_matrix[1][1]}]]")
    
    # 4. Affichage de quelques exemples de prédictions
    print("\n=== Exemples de prédictions ===")
    for i in range(min(10, results['test_size'])):
        true_label = "positif" if results['y_test'][i] == 1 else "négatif"
        pred_label = "positif" if results['y_pred'][i] == 1 else "négatif"
        correct = "✓" if true_label == pred_label else "✗"
        
        print(f"{correct} Text: \"{results['X_test'][i]}\"")
        print(f"   Vrai sentiment: {true_label}")
        print(f"   Prédit: {pred_label}")
        print("")

    # 5. Test avec de nouveaux exemples
    print("\n=== Test avec de nouveaux exemples ===")
    new_texts = [
        "Ce politicien est remarquable, il a vraiment fait avancer les choses!",
        "Je déteste sa politique, il ne fait que mentir au peuple.",
        "Une performance moyenne, ni excellente ni désastreuse.",
        "il est gentil"
    ]
    
    predictions = analyzer.predict(new_texts)
    
    for pred in predictions:
        print(f"Texte: \"{pred['text']}\"")
        print(f"  Sentiment prédit: {pred['sentiment']}")
        print(f"  Confiance: {pred['confidence']:.4f}")
        print("")

if __name__ == "__main__":
    main() 