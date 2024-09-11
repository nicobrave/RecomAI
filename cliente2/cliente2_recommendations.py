import openai
import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar la API key de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_recomendacion_cultivo(lat, lon):
    fecha = datetime.datetime.now()
    estacion = "primavera" if 3 <= fecha.month <= 5 else "verano" if 6 <= fecha.month <= 8 else "otoño" if 9 <= fecha.month <= 11 else "invierno"

    prompt = f"Estoy ubicado en las coordenadas latitud {lat} y longitud {lon}. Es {estacion} y me gustaría saber qué cultivos puedo plantar en mi zona en esta temporada."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Cambiamos a la API de chat
            messages=[
                {"role": "system", "content": "Eres un experto en cultivos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error al generar la recomendación: {str(e)}"
