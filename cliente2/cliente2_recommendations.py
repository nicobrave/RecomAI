import openai
import datetime
import os
import pdfplumber
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar la API key de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ruta al PDF
pdf_path = r"C:\Users\Usuario\Desktop\RecomAI\cliente2\Suelos-de-Chile.pdf"

def extraer_texto_pdf(pdf_path):
    """Extrae el texto de un archivo PDF usando pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            texto = ''
            for page in pdf.pages:
                texto += page.extract_text()
        return texto.strip()
    except Exception as e:
        return f"Error al extraer texto del PDF: {str(e)}"

def generar_recomendacion_comercial(texto_extraido, lat, lon):
    """Genera una recomendación comercial basada en el texto extraído del PDF."""
    fecha = datetime.datetime.now()
    estacion = "primavera" if 3 <= fecha.month <= 5 else "verano" if 6 <= fecha.month <= 8 else "otoño" if 9 <= fecha.month <= 11 else "invierno"
    
    prompt = (
        f"Estoy en las coordenadas latitud {lat} y longitud {lon}, "
        f"deseo obtener recomendaciones comerciales basadas en el informe del suelo en Chile. "
        f"El informe contiene el siguiente texto:\n\n{texto_extraido}\n\n"
        "Con base en este informe, proporciona una recomendación sobre los cultivos más rentables que se pueden plantar, "
        f"teniendo en cuenta que estamos en la temporada de {estacion}."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asesor agrícola experto en cultivos rentables para pequeños agricultores."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.2  # Menor aleatoriedad para obtener respuestas más concisas
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error al generar la recomendación: {str(e)}"

def generar_recomendacion_cultivo(lat, lon):
    # Extraer texto del PDF
    texto_pdf = extraer_texto_pdf(pdf_path)
    if "Error" in texto_pdf:
        return texto_pdf

    # Generar recomendación comercial basada en el PDF
    recomendacion = generar_recomendacion_comercial(texto_pdf, lat, lon)
    return recomendacion
