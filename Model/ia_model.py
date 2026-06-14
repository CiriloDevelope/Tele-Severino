from dotenv import load_dotenv
import os
import google.generativeai as genai

#Carrega as variáveis do .env
load_dotenv()

# Obtém a chave da API
api_key = os.getenv("GEMINI_API_KEY")
 
# Configura o Gemini
genai.configure(api_key=api_key)

print("CHAVE:", api_key)


def gerar_resposta_ia(pergunta):
    try:
        # Cria o modelo
        modelo = genai.GenerativeModel("gemini-1.5-flash")

        # Envia a pergunta
        resposta = modelo.generate_content(pergunta)

        # Retorna apenas o texto
        return {
            "resposta": resposta.text
        }

    except Exception as erro:
        return {
            "erro": str(erro)
        }