import os
from dotenv import load_dotenv
from groq import Groq  # Mudou de google.generativeai para groq

# Carrega as variáveis do .env
load_dotenv()

# Obtém a chave da API (Certifique-se de ter a GROQ_API_KEY no seu arquivo .env)
api_key = os.getenv("GROQ_API_KEY")

# Configura o cliente Groq
client = Groq(api_key=api_key)

#print("CHAVE:", api_key)


def gerar_resposta_ia(pergunta):
    try:
        # Envia a pergunta usando o modelo atualizado da Groq
        resposta = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Modelo gratuito e ativo
            messages=[
                {
                    "role": "user",
                    "content": pergunta,
                }  # Passa a sua variável 'pergunta'
            ],
            stream=False,
        )

        # Retorna apenas o texto no mesmo formato do seu código original
        return {"resposta": resposta.choices[0].message.content}

    except Exception as erro:
        return {"erro": str(erro)}