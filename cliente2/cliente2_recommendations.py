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
        f"Como un agricultor ubicado en las coordenadas latitud {lat} y longitud {lon}, "
        f"deseo conocer los cultivos más adecuados para plantar durante la temporada de {estacion}. "
        "Por favor, proporciona una recomendación detallada que incluya tipos de cultivos, "
        "condiciones climáticas favorables, y consejos prácticos para optimizar la producción. La respuesta debe ajustarse a 300 tokens y no debe contener elementos de resalte de texto ni nada parecido. Explica la recomendación fácilmente."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Cambiamos a la API de chat
            messages=[
                {"role": "system", "content": "Eres ingeniero agrónomo y un experto en agricultura y cultivos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error al generar la recomendación: {str(e)}"
