from flask import Flask, render_template
from sysinfo import SystemInfo
from digger import app as digger_app
from skybouncer import app as skybouncer_app
from inspector import app as inspector_app

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            system_info = SystemInfo()
            return render_template("home.html", system_info=system_info)
        
        self.app.register_blueprint(digger_app,     url_prefix='/digger')
        self.app.register_blueprint(skybouncer_app, url_prefix='/skybouncer')
        self.app.register_blueprint(inspector_app,  url_prefix='/inspector')

    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    server = Server()
    server.run()
