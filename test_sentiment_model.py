#!/usr/bin/env python3
"""
Script pour tester le modèle d'analyse de sentiment
"""
import sys
import os

# Ajouter le répertoire src au chemin de recherche des modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# Importer le module de test de sentiment
from ml.test_sentiment import main

if __name__ == "__main__":
    main() 