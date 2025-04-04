from flask import Blueprint
from .routes import app as digger_app

app = Blueprint('digger', __name__)
app.register_blueprint(digger_app) 