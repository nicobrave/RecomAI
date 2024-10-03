from flask import Blueprint, render_template, request, jsonify
from flask_cors import cross_origin, CORS
from workid.recommendations import generar_recomendacion_openai, df_trabajadores
from auth import validar_api_key  # Ensure this import is correct

workid_bp = Blueprint('workid', __name__, template_folder='templates', static_folder='static')

@workid_bp.route('/')
def home():
    return render_template('workid/index.html')

@workid_bp.route('/recomendaciones', methods=['GET', 'OPTIONS'])
@cross_origin(origins='https://www.recomai.cl')
def obtener_recomendaciones():
    # Validate API key
    try:
        usuario = validar_api_key()  # No need to pass request explicitly since Flask handles it globally
    except Exception as e:
        return jsonify({"error": str(e)}), 403

    # Process the request as usual after validating the API key
    cargo = request.args.get('cargo')
    if not cargo:
        return jsonify({"error": "El parámetro 'cargo' es requerido"}), 400

    # Obtener los parámetros de la solicitud
    comuna = request.args.get('comuna')
    nivel_estudio = request.args.get('nivel_estudio')
    detalle_experiencia = request.args.get('detalle_experiencia')

    # Llamar a la función para generar la recomendación
    recomendacion = generar_recomendacion_openai(
        df_trabajadores,
        cargo=cargo,
        comuna=comuna,
        nivel_estudio=nivel_estudio,
        detalle_experiencia=detalle_experiencia
    )

    return jsonify(recomendacion)
