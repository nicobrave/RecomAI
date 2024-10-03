from flask import Flask, render_template
from flask_cors import CORS
from pathlib import Path

# Importa los blueprints
from cliente2.cliente2_routes import cliente2_bp
from workid.workid_routes import workid_bp
from cliente3.cliente3_routes import cliente3_bp
from database import init_db_recomai, init_db_factura
from fuego.fuego_routes import fuego_bp
from cv.cv_routes import cv_bp
from carnet.carnet_routes import carnet_bp

# Inicializar la app Flask con las carpetas de plantillas y estáticos
app = Flask(__name__, template_folder='templates', static_folder='static')

# Inicializar las bases de datos
init_db_recomai()
init_db_factura()

# Habilitar CORS para la aplicación
CORS(app, resources={r"/*": {"origins": "https://www.recomai.cl"}})

# Registrar los blueprints con sus respectivos prefijos
app.register_blueprint(workid_bp, url_prefix='/workid')
app.register_blueprint(cliente2_bp, url_prefix='/cliente2')
app.register_blueprint(cliente3_bp, url_prefix='/cliente3')
app.register_blueprint(fuego_bp, url_prefix='/fuego')
app.register_blueprint(cv_bp, url_prefix='/cv')
app.register_blueprint(carnet_bp, url_prefix='/carnet')

# Ruta para el landing page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)