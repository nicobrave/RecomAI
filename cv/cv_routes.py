from flask import Blueprint, render_template, request, jsonify
from functools import wraps
import pytesseract
import io
from PIL import Image
import pdfplumber
import docx
import os
import openai
import json
from dotenv import load_dotenv

from auth import validar_api_key

# Middleware para validar la API key en cada solicitud
def requiere_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            usuario = validar_api_key()  # No necesitas pasar request
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 403
    return decorated_function

# Cargar variables de entorno
load_dotenv()

cv_bp = Blueprint('cv_bp', __name__, template_folder='templates', static_folder='static')

# Configurar la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Ruta para subir el CV
@cv_bp.route('/')
def home():
    return render_template('cv/upload_cv.html')

@cv_bp.route('/upload_cv', methods=['POST'])
@requiere_api_key  # Aplicar el middleware aquí
def upload_cv():
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo no válido.'}), 400

    # Extraer texto del CV (puede ser PDF, imagen o Word)
    text = extract_text_from_cv(file)
    
    # Verifica si la extracción falló
    if isinstance(text, dict) and 'error' in text:
        return jsonify(text), 400
    
    # Mejorar con OpenAI
    improved_text = improve_cv_with_openai(text)
    
    # Devolver la respuesta mejorada en JSON
    return jsonify({
        'extracted_text': text,
        'improved_text': improved_text
    })


def extract_text_from_cv(file):
    try:
        filename = file.filename.lower()

        # Procesar si es PDF
        if filename.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        
                if text:
                    print("Texto extraído de todas las páginas del PDF:", text)
                    return text

        # Procesar si es imagen
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(io.BytesIO(file.read()))
            text = pytesseract.image_to_string(image)
            print("Texto extraído de la imagen:", text)
            return text

        # Procesar si es archivo Word
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            print("Texto extraído del archivo Word:", text)
            return text

        # Si no es un formato compatible
        else:
            return {"error": "Formato de archivo no soportado. Por favor suba un PDF, imagen o archivo Word."}

    except Exception as e:
        print(f"Error al extraer texto del CV: {e}")
        return {"error": str(e)}

def improve_cv_with_openai(text):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        prompt = f"""
        Organiza el siguiente CV en un formato JSON estructurado con las siguientes secciones y formato:

        Preferencias laborales:
        - Estado laboral (buscando trabajo, trabajando, sin trabajo)
        - Fecha de disponibilidad (útil para casos de contratos a plazo fijo)
        - Zona geográfica (región)
        - Remuneración (expectativa de renta)
        - Jornadas (4x3, 5x2, 8x6, 7x7, 14x14, spot)
        - Modalidad de trabajo (remoto, híbrido, presencial, presencial faena/campamento)
        - Turno (diurno, nocturno, rotativo)

        Datos personales:
        - Nombres
        - Apellido Paterno
        - Apellido Materno
        - Tipo de identificación (RUT, RUN o Pasaporte)
        - Número de identificación (RUT,RUN)
        - Nacionalidad
        - Género
        - Fecha de nacimiento
        - Número de contacto
        - Estado civil
        - Etnia
        - Región / Provincia / Comuna
        - Dirección
        - Discapacidad (sí, no)
        - Correo
        - Número de contacto

        Educación:
        - Nivel de estudios (enseñanza básica, enseñanza media, enseñanza media técnico-profesional, técnico profesional, universitario, maestría, doctorado)
        - Institución
        - Carrera
        - Mes de inicio, año de inicio
        - Mes de finalización, año de finalización (o estudiando actualmente)

        Experiencia Laboral:
        - Nombre de la empresa
        - Categoría profesional
        - Especialidad
        - Mes de inicio, año de inicio
        - Mes de finalización, año de finalización

        Documentación:
        - Personales
        - Laborales
        - Preocupacionales y ocupacionales

        Texto del CV:
        {text}

    Si algunos de los campos no existen no los contemples en la respuesta.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en mejorar CVs y organizar su contenido en JSON estructurado."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Ajusta según la longitud de la respuesta esperada
            temperature=0.5
        )

        # Verificar si la respuesta contiene datos válidos
        content = response['choices'][0]['message']['content'].strip()
        if content:
            return json.loads(content)
        else:
            print("Respuesta vacía de OpenAI")
            return {"error": "La respuesta de OpenAI está vacía."}
    
    except Exception as e:
        print(f"Error al mejorar el CV con OpenAI: {e}")
        return {"error": str(e)}
