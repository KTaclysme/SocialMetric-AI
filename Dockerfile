FROM python:3.10-alpine
WORKDIR /code
ENV FLASK_APP=src.app
ENV FLASK_RUN_HOST=0.0.0.0

# Installation des dépendances système
RUN apk add --no-cache gcc musl-dev linux-headers g++ make tzdata dcron \
    # Dépendances pour matplotlib et autres bibliothèques graphiques
    freetype-dev jpeg-dev libpng-dev openblas-dev \
    # Polices pour les rapports PDF
    ttf-dejavu

# Configuration du fuseau horaire
RUN cp /usr/share/zoneinfo/Europe/Paris /etc/localtime
RUN echo "Europe/Paris" > /etc/timezone

# Copie des dépendances Python et installation
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Création des répertoires nécessaires
RUN mkdir -p /code/models /code/logs /code/reports /code/data

# Copie du code source
COPY . .

# Configuration du cron job pour le réentraînement hebdomadaire
RUN echo "0 0 * * 0 /usr/local/bin/python /code/train_weekly.py >> /var/log/cron.log 2>&1" > /etc/crontabs/root

# Exposition du port pour l'API
EXPOSE 5000

# Démarrage du service cron et de l'application Flask
CMD sh -c "crond -b -l 8 && echo 'Cron job configuré pour réentrainer le modèle tous les dimanches à minuit' && flask run --debug"