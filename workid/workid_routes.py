from flask import Blueprint, render_template

workid_bp = Blueprint('workid', __name__, template_folder='templates', static_folder='static')

@workid_bp.route('/')
def home():
    return render_template('index.html')
