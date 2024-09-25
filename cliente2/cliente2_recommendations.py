import openai
import datetime
import os
import pdfplumber
import requests
import io
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar la API key de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# Descargar el PDF desde Google Drive
def descargar_pdf_desde_drive():
    url = "https://drive.google.com/uc?export=download&id=1bwSOmhtswQ-4kpDPThisCgQTTAPHlRnE"
    response = requests.get(url)

    if response.status_code == 200:
        pdf_data = io.BytesIO(response.content)
        return pdf_data
    else:
        print(f"Error al descargar el PDF: {response.status_code}")
        return None

def extraer_texto_pdf(pdf_data):
    """Extrae el texto de un archivo PDF usando pdfplumber."""
    try:
        with pdfplumber.open(pdf_data) as pdf:
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
    # Descargar y extraer el texto del PDF desde Google Drive
    pdf_data = descargar_pdf_desde_drive()
    if not pdf_data:
        return "Error al descargar el archivo PDF."

    texto_pdf = extraer_texto_pdf(pdf_data)
    if "Error" in texto_pdf:
        return texto_pdf

    # Generar recomendación comercial basada en el PDF
    recomendacion = generar_recomendacion_comercial(texto_pdf, lat, lon)
    return recomendacion
