from dotenv import load_dotenv
import os
import openai

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Asignar la API key de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    raise ValueError("La API key de OpenAI no está configurada. Verifica tu archivo .env.")
