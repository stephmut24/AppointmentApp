import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='gestion_hopital',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("Connexion réussie")
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users LIMIT 1;")
            row = cursor.fetchone()
            print("Premier utilisateur dans la base de données:", row)
    except Error as e:
        print(f"Erreur: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connexion fermée")

if __name__ == "__main__":
    test_connection()
