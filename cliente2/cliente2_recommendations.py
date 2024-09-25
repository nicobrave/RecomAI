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

    prompt = (
    f"Soy un agricultor en las coordenadas latitud {lat} y longitud {lon}, "
    f"deseo conocer los cultivos más rentables para la temporada de {estacion}. "
    "Proporciona una respuesta breve y concisa con máximo 3 cultivos rentables, sus condiciones climáticas y un consejo práctico por cada uno. "
    "La respuesta debe ser de menos de 1000 caracteres."
    "Inspirate en el pdf Suelos de Chile si necesitas complementar la información de manera más precisa"
)

    try:
        response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Eres ingeniero agrónomo y un experto en cultivos rentables."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=300,
    temperature=0.2  # Menor aleatoriedad para obtener respuestas más concisas
)
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error al generar la recomendación: {str(e)}"