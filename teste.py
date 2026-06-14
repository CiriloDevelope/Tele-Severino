from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

modelo = genai.GenerativeModel("gemini-2.0-flash")

resposta = modelo.generate_content("Olá")

print(resposta.text)