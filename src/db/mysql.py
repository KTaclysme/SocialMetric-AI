import os
import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "user"),
        password=os.getenv("MYSQL_PASSWORD", "password"),
        database=os.getenv("MYSQL_DB", "mydb")
    )

def get_mysql_connection():
    try:
        cnx = create_connection()
        if cnx.is_connected():
            print("Connexion réussie à MySQL !")
            return cnx
    except mysql.connector.Error as err:
        print(f"Impossible de se connecter à MySQL : {err}")
        return None
    
def create_table():
    cnx = get_mysql_connection()
    if cnx is None:
        return print({'error': 'Unable to connect to the database'}), 500
    
    cur = cnx.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS tweets (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        text VARCHAR(255), 
        positive INT DEFAULT 0, 
        negative INT DEFAULT 0)''')
    cnx.commit()
    cur.close()
    cnx.close()
    return print({'message': 'Table created successfully'})