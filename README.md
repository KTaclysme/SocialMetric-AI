# SocialMetric-AI

required:
python
docker

setup project:
python3 -m venv .venv
pip install -r requirements.txt

run project:
docker compose up --build
docker compose down -v

train model:
docker exec -it tp-final-web-1 python /code/train.py

predict model:
docker exec -it tp-final-web-1 python /code/predict.py

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
