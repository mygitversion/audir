from flask import Flask, render_template, request, redirect, url_for
from webapp.model import db 
from werkzeug.utils import secure_filename
import os

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/', methods=["GET","POST"])
    def index():                    
        if request.method == 'POST':
            uploaded_file = request.files['file_name']
            filename = secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1]
    
            if filename and (file_ext in app.config['ALLOWED_UPLOAD_EXTENSIONS']):
                path_to_save = os.path.join(app.config['UPLOAD_PATH'],filename)
                uploaded_file.save(path_to_save)
            return redirect(url_for('index'))

        return render_template("index.html")

   
    @app.errorhandler(413)
    def too_large(e):
        return "File is too large", 413


    return app