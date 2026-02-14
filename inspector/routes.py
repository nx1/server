from flask import Blueprint, render_template
from inspection import get_all_installed_modules, inspect

app = Blueprint('routes', __name__)

@app.route('/')
def index():
    return render_template('modules.html', installed_modules=get_all_installed_modules(), inspect_res=[])

@app.route('/<module>')
def view_module(module):
    inspect_res = inspect(module)
    return render_template('modules.html', installed_modules=get_all_installed_modules(), inspect_res=inspect_res)