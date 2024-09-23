from flask import Blueprint, render_template, request, jsonify
from cliente3.cliente3_recommendations import process_invoice

cliente3_bp = Blueprint('cliente3_bp', __name__, template_folder='templates', static_folder='static')

@cliente3_bp.route('/')
def home():
    return render_template('cliente3/upload.html')

@cliente3_bp.route('/upload_invoice', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo no válido.'}), 400
    result = process_invoice(file)
    return jsonify(result)
