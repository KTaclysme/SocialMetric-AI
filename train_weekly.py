#!/usr/bin/env python3
import sys
import os
import logging
import datetime
import pickle

# Configuration du logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"model_retraining_{datetime.datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from ml.sentiment_model import SentimentAnalyzer
from db.mysql import get_mysql_connection


def retrain_model():
    try:
        analyzer = SentimentAnalyzer()
        cnx = get_mysql_connection()

        if cnx is None:
            logging.error("Impossible de se connecter à la base de données")
            return False

        cur = cnx.cursor(dictionary=True)
        cur.execute('''SELECT * FROM tweets''')
        data = cur.fetchall()
        cur.close()
        cnx.close()

        if not data:
            logging.warning("Aucune donnée disponible pour l'entraînement")
            return False

        texts, labels = analyzer.load_data(db_data=data)
        results = analyzer.train(texts, labels)

        models_dir = os.path.join(current_dir, "models")
        os.makedirs(models_dir, exist_ok=True)

        model_path = os.path.join(models_dir, "sentiment_model_latest.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': analyzer.model,
                'vectorizer': analyzer.vectorizer,
                'training_date': datetime.datetime.now().isoformat(),
                'metrics': {
                    'accuracy': results['accuracy'],
                    'classification_report': results['classification_report']
                }
            }, f)

        logging.info(f"Modèle réentraîné avec succès. Précision: {results['accuracy']:.4f}")

        from report_generator import generate_evaluation_report
        report_path = os.path.join(current_dir, "reports",
                                   f"evaluation_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        os.makedirs(os.path.join(current_dir, "reports"), exist_ok=True)
        generate_evaluation_report(results, report_path)
        logging.info(f"Rapport d'évaluation généré: {report_path}")

        return True

    except Exception as e:
        logging.error(f"Erreur lors du réentraînement: {str(e)}")
        return False


if __name__ == "__main__":
    logging.info("Début du réentraînement hebdomadaire")
    success = retrain_model()
    if success:
        logging.info("Réentraînement terminé avec succès")
    else:
        logging.error("Échec du réentraînement")