import sys
import os
import logging
import datetime
from app import *

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

train_model()


if __name__ == "__main__":
    logging.info("Début du réentraînement hebdomadaire")
    success = train_model()
    if success:
        logging.info("Réentraînement terminé avec succès")
    else:
        logging.error("Échec du réentraînement")