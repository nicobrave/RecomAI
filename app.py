from flask import Flask, render_template
from flask_cors import CORS
from pathlib import Path

# Importa los blueprints
from cliente2.cliente2_routes import cliente2_bp  # Asegúrate que el import está correcto
from workid.workid_routes import workid_bp  # Asegúrate que el import está correcto

app = Flask(__name__, template_folder='templates', static_folder='static')

app.template_folder = Path(app.template_folder).parent / 'templates'


CORS(app)

# Registrar los blueprints con sus respectivos prefijos
app.register_blueprint(workid_bp, url_prefix='/workid')
app.register_blueprint(cliente2_bp, url_prefix='/cliente2')

# Ruta para el landing page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
