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
    f"Soy un agricultor en las coordenadas latitud {lat} y longitud {lon}. "
    f"Deseo saber los cultivos más rentables para la temporada de {estacion}. "
    "Por favor, da una recomendación precisa que incluya el tipo de cultivo más rentable, "
    "condiciones climáticas favorables y consejos breves para maximizar la producción. "
    "Limita la respuesta a 300 tokens y no incluyas detalles innecesarios o resaltados."
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
