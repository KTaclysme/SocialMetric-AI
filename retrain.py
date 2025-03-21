import schedule
import time
from train import train_model
from datetime import datetime

def retrain_job():
    print(f"\nDémarrage du réentraînement - {datetime.now()}")
    try:
        train_model()
        print(f"Réentraînement terminé avec succès - {datetime.now()}")
    except Exception as e:
        print(f"Erreur lors du réentraînement: {str(e)}")

def main():
    print("Démarrage du planificateur de réentraînement...")
    
    # Planifie le réentraînement tous les lundis à 3h du matin
    schedule.every().monday.at("03:00").do(retrain_job)
    
    # Exécute un premier entraînement au démarrage
    retrain_job()
    
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Vérifie toutes les heures

if __name__ == "__main__":
    main() 