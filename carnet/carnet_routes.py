from flask import Blueprint, render_template, request, jsonify
from functools import wraps
import openai
import json
from dotenv import load_dotenv
from google.cloud import vision, storage
import os
import io

from auth import validar_api_key 

# Middleware para validar la API key en cada solicitud
def requiere_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({'error': 'API key requerida'}), 400

        usuario = validar_api_key()  # Llamar a la función sin pasar request
        if not usuario:
            return jsonify({'error': 'API key inválida'}), 403

        # Continuar si la API key es válida
        return f(*args, **kwargs)
    return decorated_function

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/Usuario/Desktop/RecomAI/carnet/recomai-437320-927be399c83f.json"

carnet_bp = Blueprint('carnet_bp', __name__, template_folder='templates/carnet', static_folder='static/carnet')

@carnet_bp.route('/')
def home():
    return render_template('carnet/upload_carnet.html')

@carnet_bp.route('/upload_carnet', methods=['POST'])
@requiere_api_key  # Middleware aplicado aquí
def upload_carnet():
    
    usuario = validar_api_key

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó ningún archivo.'}), 400

        file = request.files['file']
        
        # Verificar si el archivo fue cargado
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo no válido.'}), 400

        filename = file.filename.lower()
        print(f"Archivo recibido: {filename}")

        # Subir archivo a Google Cloud Storage
        bucket_name = "recomai"  # Reemplaza con tu bucket
        destination_blob_name = filename
        gcs_uri = upload_file_to_gcs(file, bucket_name, destination_blob_name)

        # Procesar el PDF con Google Cloud Vision y obtener el output_uri
        output_uri = extract_text_from_pdf(gcs_uri)

        if isinstance(output_uri, dict) and 'error' in output_uri:
            return jsonify(output_uri), 400

        # Descargar los resultados del procesamiento almacenados en GCS
        extracted_text = download_and_process_output(output_uri)

        # Si el texto está vacío o hay un problema, retornar un error
        if not extracted_text:
            return jsonify({'error': 'No se pudo extraer texto del archivo.'}), 400

        # Mejorar con OpenAI (ahora con el texto extraído, no la URL)
        improved_text = improve_with_openai(extracted_text)

        return jsonify({
            'extracted_text': extracted_text,
            'improved_text': improved_text
        })

    except Exception as e:
        # Agrega este bloque para ver los detalles completos del error
        print(f"Error durante el procesamiento: {str(e)}")
        return jsonify({'error': f'Hubo un error al procesar el archivo: {str(e)}'}), 500

# Función para filtrar solo la información relevante de la cédula de identidad
def extract_relevant_cedula_info(text):
    lines = text.split('\n')
    relevant_info = {}
    
    for line in lines:
        if "Apellidos" in line:
            relevant_info["Apellidos"] = line.split(":")[-1].strip()
        if "Nombres" in line:
            relevant_info["Nombres"] = line.split(":")[-1].strip()
        if "Nacionalidad" in line:
            relevant_info["Nacionalidad"] = line.split(":")[-1].strip()
        if "Fecha de Nacimiento" in line:
            relevant_info["Fecha_de_Nacimiento"] = line.split(":")[-1].strip()
        if "Fecha de Emisión" in line:
            relevant_info["Fecha_de_Emision"] = line.split(":")[-1].strip()
        if "Fecha de Vencimiento" in line:
            relevant_info["Fecha_de_Vencimiento"] = line.split(":")[-1].strip()
        if "RUN" in line:
            relevant_info["RUN"] = line.split(":")[-1].strip()
        if "Número de Documento" in line:
            relevant_info["Numero_Documento"] = line.split(":")[-1].strip()
        if "Nació en" in line:
            relevant_info["Nacio_en"] = line.split(":")[-1].strip()
        if "Profesión" in line:
            relevant_info["Profesion"] = line.split(":")[-1].strip()

    return relevant_info if relevant_info else "No se encontraron datos relevantes."

def download_and_process_output(output_uri):
    try:
        # Inicializar cliente de Google Cloud Storage
        storage_client = storage.Client()

        # Extraer el bucket y el nombre del archivo desde la URI
        bucket_name = output_uri.split("/")[2]
        prefix = "/".join(output_uri.split("/")[3:])

        bucket = storage_client.bucket(bucket_name)

        # Descargar los archivos JSON con los resultados
        blobs = list(bucket.list_blobs(prefix=prefix))
        extracted_text = ""

        for blob in blobs:
            print(f"Descargando archivo de resultados: {blob.name}")
            content = blob.download_as_string()
            response_data = json.loads(content)
            for annotation in response_data['responses']:
                if 'fullTextAnnotation' in annotation:
                    extracted_text += annotation['fullTextAnnotation']['text']

        return extracted_text if extracted_text else "No se encontró texto en el PDF."

    except Exception as e:
        print(f"Error al descargar los resultados: {e}")
        return {"error": str(e)}

# Función para mejorar el texto extraído usando OpenAI
def improve_with_openai(filtered_data):
    try:
        if not filtered_data:
            print("El texto extraído está vacío o no es válido.")
            return {"error": "El texto extraído está vacío o no es válido."}

        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = f"""
        Organiza la siguiente información extraída de una cédula de identidad chilena en un formato JSON estructurado. Asegúrate de incluir los siguientes campos: 
        apellidos, fechaEmision, fechaNacimiento, fechaVencimiento, firma, lugarEmision, nacionalidad, nombres, numeroDocumento, pais, run, servicioRegistro, sexo, tipoDocumento.
        
        {json.dumps(filtered_data, indent=4)}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en documentos de identidad."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.5
        )

        # Verificar si la respuesta contiene contenido
        if response and 'choices' in response and response['choices']:
            content = response['choices'][0]['message']['content'].strip()

            # Intentar convertir el contenido solo si parece ser un JSON
            if content.startswith('{') and content.endswith('}'):
                return json.loads(content)  # Intentar convertir el contenido a JSON
            else:
                return {"formatted_text": content}

    except Exception as e:
        print(f"Error al mejorar el Doc con OpenAI: {str(e)}")
        return {"error": str(e)}

# Función para subir el archivo a Google Cloud Storage
def upload_file_to_gcs(file, bucket_name, destination_blob_name):
    """Sube un archivo a Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(file)

    print(f"Archivo subido a gs://{bucket_name}/{destination_blob_name}")
    return f"gs://{bucket_name}/{destination_blob_name}"

# Función para extraer texto de un PDF utilizando Google Cloud Vision directamente
def extract_text_from_pdf(gcs_uri):
    try:
        client = vision.ImageAnnotatorClient()

        # Configuración de entrada desde Google Cloud Storage
        gcs_source = vision.GcsSource(uri=gcs_uri)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type="application/pdf")

        # Configuración de salida (OutputConfig) para almacenar los resultados en GCS
        output_gcs_uri = "gs://recomai_respuestas/"  # Reemplaza con tu bucket de resultados
        output_config = vision.OutputConfig(gcs_destination=vision.GcsDestination(uri=output_gcs_uri), batch_size=1)

        # Configurar la solicitud de procesamiento asíncrono
        async_request = vision.AsyncAnnotateFileRequest(
            input_config=input_config,
            features=[vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
            output_config=output_config
        )

        # Enviar la solicitud a Google Cloud Vision
        operation = client.async_batch_annotate_files(requests=[async_request])

        # Esperar a que se complete la operación
        result = operation.result(timeout=300)

        # Devolver la URI de los resultados almacenados
        for resp in result.responses:
            if resp.output_config:
                print(f"Los resultados se almacenaron en {resp.output_config.gcs_destination.uri}")
                return resp.output_config.gcs_destination.uri
            else:
                return {"error": "No se encontraron resultados en el PDF."}

    except Exception as e:
        print(f"Error al procesar el PDF con Google Cloud Vision: {e}")
        return {"error": str(e)}
