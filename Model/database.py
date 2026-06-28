import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def conectar_banco():
    try:
        cnx = mysql.connector.connect(
            user=os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root"),
            password=os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", ""),
            host=os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306")),
            database=os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "tele_severino"),
        )
        return cnx

    except mysql.connector.Error as erro:
        print(f"Erro ao conectar no banco: {erro}")
        return None


if __name__ == "__main__":
    conexao = conectar_banco()
    if conexao:
        print("Conexão com o banco realizada com sucesso.")
        conexao.close()
