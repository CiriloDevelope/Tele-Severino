import mysql.connector

def conectar_banco():
    try:
        # Cria a conexão com o banco de dados
        cnx = mysql.connector.connect(
            user='root', 
            password='', 
            host='localhost', 
            database='tele_severino'  
        )
        return cnx
        
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar: {erro}")

if __name__ == "__main__":
    conectar_banco()