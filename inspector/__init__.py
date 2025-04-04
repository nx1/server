from flask import Blueprint
from .routes import app as inspector_app

app = Blueprint('inspector', __name__)
app.register_blueprint(inspector_app) 