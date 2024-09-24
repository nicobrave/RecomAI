from flask import Blueprint, render_template, request, jsonify
from cliente2.cliente2_recommendations import generar_recomendacion_cultivo

cliente2_bp = Blueprint('cliente2', __name__, template_folder='templates', static_folder='static')

@cliente2_bp.route('/')
def home():
    return render_template('cliente2/index.html')

@cliente2_bp.route('/recomendacion-cultivo', methods=['GET'])
def obtener_recomendacion_cultivo():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    if lat is None or lon is None:
        return jsonify({"error": "Latitud y longitud son requeridas"}), 400
    
    # Llamar a la función generar_recomendacion_cultivo para obtener la recomendación
    recomendacion = generar_recomendacion_cultivo(lat, lon)
    return jsonify({"recomendacion": recomendacion})
