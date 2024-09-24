from flask import Blueprint, jsonify, request, render_template
from .fuego_recommendations import obtener_recomendacion_fuego

fuego_bp = Blueprint('fuego', __name__)

@fuego_bp.route('/recommendacion', methods=['POST'])
def recomendaciones_fuego():
    try:
        # Recibir los datos enviados en formato JSON
        data = request.get_json()
        print(f"Datos recibidos: {data}")  # Verificar que los datos se están recibiendo

        # Intentar extraer la latitud y longitud
        try:
            lat = float(data['lat'])
            lon = float(data['lon'])
            print(f"Latitud: {lat}, Longitud: {lon}")  # Verificar que las coordenadas se están obteniendo correctamente
        except ValueError as ve:
            print(f"Error al convertir lat y lon a float: {ve}")
            return jsonify({"error": f"Error al convertir latitud/longitud: {str(ve)}"}), 400

        # Intentar obtener la recomendación y el mapa
        try:
            recomendacion, mapa_path = obtener_recomendacion_fuego(lat, lon)
            print(f"Recomendación generada: {recomendacion}, Mapa generado: {mapa_path}")
        except Exception as e:
            print(f"Error al generar recomendación o mapa: {e}")
            return jsonify({"error": f"Error al generar recomendación/mapa: {str(e)}"}), 500

        # Retornar recomendación y el enlace del mapa si fue generado
        if recomendacion and mapa_path:
            return jsonify({'recomendacion': recomendacion, 'mapa_url': mapa_path}), 200
        elif recomendacion:
            return jsonify({'recomendacion': recomendacion}), 200
        else:
            return jsonify({"error": "No se pudo generar la recomendación."}), 500

    except Exception as e:
        print(f"Error general en la ruta /recommendacion: {e}")
        return jsonify({"error": f"Error en la solicitud: {str(e)}"}), 400

@fuego_bp.route('/')
def index():
    return render_template('fuego/index.html')
