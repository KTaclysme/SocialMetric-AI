# SocialMetric-AI

SocialMetric-AI est un projet d'analyse de sentiment basé sur une régression logistique.

## Description

Ce projet utilise scikit-learn pour analyser le sentiment de tweets. Il implémente une régression logistique pour classifier les tweets en sentiments "positifs" ou "négatifs".

## Installation

1. Cloner le dépôt
2. Assurez-vous d'avoir Docker et Docker Compose installés sur votre machine

## Utilisation

### Lancement de l'application

1. Démarrer l'application avec Docker Compose :
   ```
   docker compose up --build
   ```

2. Initialiser la base de données :
   ```
   POST http://localhost:5000/data
   ```
   Cette étape est nécessaire pour créer les données initiales dans la base de données.

   Corps de la requête :
   ```json
   [
        {
            "text": "les ciminels ont bafoués nos droit",
            "positive": 0,
            "negative": 1
        },
        {
            "text": "Un bon système politique peut garantir la stabilité et la prospérité d'un pays.",
            "positive": 1,
            "negative": 0
        },
        {
            "text": "J'admire vraiment son leadership, il est exceptionnel !",
            "positive": 1,
            "negative": 0
        }
   ]
   ```

   Note : Ces données d'exemple doivent être copiées dans un fichier `tweets_data.json` dans le dossier `data/` de votre projet avant de lancer l'application.

3. Entraîner le modèle (si ce n'est pas déjà fait) :
   ```
   POST http://localhost:5000/sentiment/train
   ```

L'application sera accessible à l'adresse http://localhost:5000/

Pour arrêter l'application :

### Test du modèle de sentiment

Pour tester le modèle de sentiment indépendamment de l'application:

```
python test_sentiment_model.py
```

### API d'analyse de sentiment

L'API expose les points d'accès suivants:

#### 1. Entraîner le modèle

```
POST /sentiment/train
```
Corps de la requête:
```json
{
        "text": "J'admire vraiment son leadership, il est exceptionnel !",
        "positive": 1,
        "negative": 0
}
```

Entraîne le modèle sur les données de la base de données et retourne les métriques de performance.

#### 2. Prédire le sentiment d'un texte

```
POST /sentiment/predict
```

Corps de la requête:
```json
{
  "text": "Votre texte à analyser"
}
```

#### 3. Prédiction en masse

```
POST /sentiment/bulk-predict
```

Corps de la requête:
```json
{
  "texts": ["Texte 1", "Texte 2", "..."]
}
```

#### 4. Entraîner le modèle via URL

```
GET /sentiment/train-url?text=Votre+texte&sentiment=positive
```

Ajoute un nouvel exemple à la base de données, réentraîne le modèle et retourne les métriques de performance.

Paramètres:
- `text`: Le texte à analyser
- `sentiment`: Le sentiment associé (`positive` ou `negative`)

#### 5. Entraîner le modèle avec plusieurs exemples via URL

```
GET /sentiment/train-batch-url?data={"texts":["Texte 1","Texte 2"],"sentiments":["positive","negative"]}
```

Ajoute plusieurs exemples à la base de données, réentraîne le modèle et retourne les métriques de performance.

Paramètre:
- `data`: Chaîne JSON contenant les listes `texts` et `sentiments`

#### 6. Prédire le sentiment d'un texte via URL

```
GET /sentiment/predict-url?text=Votre+texte+à+analyser
```

Analyse le sentiment du texte fourni et retourne le résultat.

Paramètre:
- `text`: Le texte à analyser

## Fonctionnement technique

- Le modèle utilise une régression logistique de scikit-learn
- Les textes sont vectorisés en utilisant TF-IDF (Term Frequency-Inverse Document Frequency)
- Une liste de stop words français est utilisée pour filtrer les mots non significatifs
- Les métriques d'évaluation incluent la précision (accuracy), le rappel, le F1-score et la matrice de confusion

required: 
python 
docker

setup project: 
python3 -m venv .venv 
pip install -r requirements.txt

run project:
docker compose up --build
docker compose down -v 

routes: 
localhost:5000
[GET] localhost:5000/data => show all data
[POST] localhost:5000/data => add data

db:
mysql 
table tweets 
rows: 
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY 
    text VARCHAR(255), 
    positive INT DEFAULT 0, 
    negative INT DEFAULT 0
