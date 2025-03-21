FROM python:3.10-alpine
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Installation des dépendances système nécessaires pour scikit-learn
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    build-base \
    python3-dev

# Installation des dépendances Python
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000
COPY . .
CMD ["flask", "run", "--debug"]