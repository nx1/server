from flask import Flask, render_template
from sysinfo import SystemInfo
from digger import app as digger_app

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            system_info = SystemInfo()
            return render_template("home.html", system_info=system_info)
        
        # Register the digger blueprint
        self.app.register_blueprint(digger_app, url_prefix='/digger')

    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)


