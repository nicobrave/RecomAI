from flask import Blueprint, render_template, request, jsonify
from flask_cors import cross_origin
from workid.recommendations import generar_recomendacion_openai, df_trabajadores

workid_bp = Blueprint('workid', __name__, template_folder='templates', static_folder='static')

@workid_bp.route('/')
def home():
    return render_template('workid/index.html')

@workid_bp.route('/recomendaciones', methods=['GET', 'OPTIONS'])
@cross_origin(origins='https://www.recomai.cl')
def obtener_recomendaciones():
    if request.method == 'OPTIONS':
        return '', 200

    # Obtener los parámetros de la solicitud
    cargo = request.args.get('cargo')
    comuna = request.args.get('comuna')
    nivel_estudio = request.args.get('nivel_estudio')
    detalle_experiencia = request.args.get('detalle_experiencia')

    if not cargo:
        return jsonify({"error": "El parámetro 'cargo' es requerido"}), 400

    # Llamar a la función para generar la recomendación
    recomendacion = generar_recomendacion_openai(
        df_trabajadores,
        cargo=cargo,
        comuna=comuna,
        nivel_estudio=nivel_estudio,
        detalle_experiencia=detalle_experiencia
    )

    return jsonify(recomendacion)
