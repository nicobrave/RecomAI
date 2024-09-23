import pytesseract
import os
from PIL import Image
import io
import re
import openai
import json
from datetime import datetime
import pdfplumber

from database import (
    obtener_contrato_por_numero,
    obtener_ito_por_numero_contrato,
    insertar_factura,
    obtener_facturas_pendientes
)

from utils import send_email

# Configurar la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_invoice(file):
    try:
        if file.filename.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                if text:
                    print("Texto extraído con pdfplumber:", text)
                    return text
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        print("Texto extraído con OCR:", text)
        return text
    except Exception as e:
        print(f"Error al extraer texto de la factura: {e}")
        return ""
    
def homologar_campos(invoice_data):
    homologacion = {
        'Número de Factura': 'numero_factura',
        'Proveedor': 'proveedor',
        'Monto': 'monto',
        'Glosa': 'glosa',
        'Número de Contrato': 'contract_number',
        'Número de Orden de Compra': 'order_number',
        'Fecha de Vencimiento': 'fecha_vencimiento'
    }
    invoice_data_homologada = {}
    for key, value in invoice_data.items():
        campo_homologado = homologacion.get(key, key.lower())
        invoice_data_homologada[campo_homologado] = value
    return invoice_data_homologada

def parse_invoice_text(text):
    invoice_data = {}
    missing_fields = []
    try:
        monto_match = re.search(r'(Total Honorarios|Monto Total|Total Amount|Amount):?\s*\$?([\d,\.]+)', text, re.IGNORECASE)
        if monto_match:
            monto = monto_match.group(2).replace('.', '').replace(',', '.')
            invoice_data['monto'] = monto
        else:
            missing_fields.append('monto')

        numero_factura_match = re.search(r'(N\s*°|Número de Factura|Invoice Number|Facture No.):?\s*(\S+)', text, re.IGNORECASE)
        if numero_factura_match:
            numero_factura = numero_factura_match.group(2).strip()
            invoice_data['Número de Factura'] = numero_factura
        else:
            missing_fields.append('Número de Factura')

        proveedor_match = re.search(r'Señor\(es\):\s*([A-Z\s]+)', text, re.IGNORECASE)
        if proveedor_match:
            proveedor = proveedor_match.group(1).strip()
            invoice_data['Proveedor'] = proveedor
        else:
            missing_fields.append('Proveedor')

        glosa_match = re.search(r'Por atención profesional:\s*(.+)', text, re.IGNORECASE)
        if glosa_match:
            glosa = glosa_match.group(1).strip()
            invoice_data['Glosa'] = glosa
        else:
            missing_fields.append('Glosa')

        fecha_emision_match = re.search(r'Fecha / Hora Emisión:\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
        if fecha_emision_match:
            fecha_emision = fecha_emision_match.group(1).strip()
            invoice_data['fecha_emision'] = fecha_emision
        else:
            missing_fields.append('fecha_emision')

        print("Datos parseados de la factura:", invoice_data)
        return invoice_data, missing_fields
    except Exception as e:
        print(f"Error al parsear el texto de la factura: {e}")
        return invoice_data, missing_fields
    
def extract_invoice_details(text):
    try:
        prompt = f"""
        Extrae los siguientes datos de la factura:
        {text}

        Datos requeridos:
        - Número de Factura
        - Proveedor
        - Monto
        - Glosa
        - Número de Contrato (si aparece) 
        - Número de Orden de Compra (si aparece)
        - Fecha de Vencimiento
        
        Responde en formato JSON. Asegúrate de no confundir el "Número de Contrato" con el "Número de Orden de Compra".
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en procesamiento de facturas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0
        )
        invoice_data = json.loads(response['choices'][0]['message']['content'].strip())
        return invoice_data
    except Exception as e:
        print(f"Error al extraer detalles de la factura con OpenAI: {e}")
        return {}

def validate_invoice_data(invoice_data):
    try:
        contract = obtener_contrato_por_numero(invoice_data.get('contract_number'))

        if not contract:
            return False, "Contrato no encontrado."

        contract_order_number = contract['order_number']
        invoice_order_number = invoice_data.get('order_number', '')

        if isinstance(contract_order_number, str):
            contract_order_number = contract_order_number.strip()
        if isinstance(invoice_order_number, str):
            invoice_order_number = invoice_order_number.strip()

        if str(contract_order_number) != str(invoice_order_number):
            return False, "Orden de compra no coincide con el contrato."

        return True, "Contrato y orden de compra válidos."
    except Exception as e:
        print(f"Error al validar datos de la factura: {e}")
        return False, f"Error de validación: {e}"


def get_ito_for_contract(contract_number):
    try:
        contract = obtener_contrato_por_numero(contract_number)
        if contract:
            ito_email = contract.get('ito_email')
            if ito_email:
                return ito_email
            else:
                print(f"Contrato encontrado pero no tiene 'ito_email'.")
                return None
        else:
            print(f"Contrato no encontrado: {contract_number}")
            return None
    except Exception as e:
        print(f"Error al obtener ITO para el contrato {contract_number}: {e}")
        return None


def notify_ito(ito_email, invoice_data):
    try:
        subject = f"Nueva Factura para Revisar: {invoice_data.get('numero_factura')}"
        body = f"Estimado ITO,\n\nSe ha recibido una nueva factura que requiere su revisión.\n\nDetalles:\n{json.dumps(invoice_data, indent=2)}\n\nSaludos."
        send_email(ito_email, subject, body)
    except Exception as e:
        print(f"Error al notificar al ITO: {e}")

def process_invoice(file):
    text = extract_text_from_invoice(file)
    if not text:
        return {"error": "No se pudo extraer texto de la factura."}

    invoice_data, missing_fields_pdfplumber = parse_invoice_text(text)
    invoice_data_openai = extract_invoice_details(text)

    invoice_data_homologada_pdfplumber = homologar_campos(invoice_data)
    invoice_data_homologada_openai = homologar_campos(invoice_data_openai)

    for key, value in invoice_data_homologada_openai.items():
        if key not in invoice_data_homologada_pdfplumber or not invoice_data_homologada_pdfplumber[key]:
            invoice_data_homologada_pdfplumber[key] = value

    if 'contract_number' in invoice_data_homologada_pdfplumber:
        invoice_data_homologada_pdfplumber['contract_number'] = invoice_data_homologada_pdfplumber['contract_number'].replace("Contrato", "").strip()

    is_valid, validation_message = validate_invoice_data(invoice_data_homologada_pdfplumber)
    
    if not is_valid:
        return {
            "data": invoice_data_homologada_pdfplumber,
            "error": validation_message
        }

    ito_email = get_ito_for_contract(invoice_data_homologada_pdfplumber.get('contract_number'))

    if not ito_email:
        return {
            "data": invoice_data_homologada_pdfplumber,
            "error": "ITO correspondiente no encontrado.",
            "validation_message": validation_message
        }

    # Si todo está correcto, notificar al ITO usando el correo directamente
    notify_ito(ito_email, invoice_data_homologada_pdfplumber)

    try:
        factura_data = {
            'number': invoice_data_homologada_pdfplumber.get('numero_factura'),
            'vendor': invoice_data_homologada_pdfplumber.get('proveedor'),
            'amount': float(invoice_data_homologada_pdfplumber.get('monto', 0)),
            'glosa': invoice_data_homologada_pdfplumber.get('glosa'),
            'contract_number': invoice_data_homologada_pdfplumber.get('contract_number'),
            'due_date': datetime.strptime(invoice_data_homologada_pdfplumber.get('fecha_vencimiento'), '%d/%m/%Y'),
            'status': 'Pendiente',
            'ito_email': ito_email
        }

        # Insertar la factura y obtener el ObjectId
        result = insertar_factura([factura_data])
        factura_id = result.inserted_ids[0]  # Obtener el ObjectId

        # Convertir el ObjectId a string para poder serializarlo
        factura_data['_id'] = str(factura_id)

        return {
            "message": "Factura procesada y notificada correctamente.",
            "data": factura_data,
            "validation_message": validation_message
        }
    except Exception as e:
        print(f"Error al guardar la factura en la base de datos: {e}")
        return {"error": f"Error al guardar la factura: {e}", "data": invoice_data}
