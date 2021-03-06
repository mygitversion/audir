from flask import Flask, render_template
from webapp.model import db 

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():                    
        title = "Audir"
        return render_template("index.html", page_title=title)

    return app