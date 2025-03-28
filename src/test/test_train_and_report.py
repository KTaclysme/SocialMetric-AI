import os
import sys
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from ml.sentiment_model import SentimentAnalyzer
from db.mysql import get_mysql_connection
from report_generator import generate_evaluation_report


def main():
    logging.info("Démarrage du processus d'entraînement et génération de rapport")

    # Récupérer les données depuis la base de données
    analyzer = SentimentAnalyzer()
    cnx = get_mysql_connection()

    if cnx is None:
        logging.error("Impossible de se connecter à la base de données")
        return

    cur = cnx.cursor(dictionary=True)
    cur.execute('''SELECT * FROM tweets''')
    data = cur.fetchall()
    cur.close()
    cnx.close()

    if not data:
        logging.error("Aucune donnée disponible pour l'entraînement")
        return

    # Charger et entraîner
    logging.info(f"Chargement des données d'entraînement ({len(data)} exemples)...")
    texts, labels = analyzer.load_data(db_data=data)
    logging.info(f"Entraînement du modèle avec {len(texts)} exemples...")
    results = analyzer.train(texts, labels)

    # Générer le rapport
    logging.info("Génération du rapport d'évaluation...")
    report_path = generate_evaluation_report(results)
    logging.info(f"Rapport généré avec succès: {report_path}")

    # Afficher quelques statistiques
    logging.info(f"Précision du modèle: {results['accuracy']:.4f}")
    logging.info(f"F1-score (positif): {results['classification_report']['positif']['f1-score']:.4f}")
    logging.info(f"F1-score (négatif): {results['classification_report']['négatif']['f1-score']:.4f}")


if __name__ == "__main__":
    main()