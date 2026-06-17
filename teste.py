import os
from dotenv import load_dotenv
from groq import Groq  # Importa a biblioteca oficial da Groq

# 1. Carrega as variáveis do arquivo .env
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# 2. Inicializa o cliente oficial da Groq (não precisa passar base_url)
client = Groq(api_key=api_key)

try:
    # 3. Envia a mensagem usando o modelo gratuito Llama 3
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Modelo rápido e gratuito da Meta na Groq
        messages=[
            {"role": "system", "content": "Você é um assistente prestativo em português."},
            {"role": "user", "content": "Olá! Explique de forma simples o que é uma API."}
        ],
        stream=False
    )

    print("Resposta da Groq (Llama 3):")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"Erro ao chamar a Groq: {e}")