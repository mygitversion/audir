from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime as dt
from webapp.model import db, Audir_data
from werkzeug.utils import secure_filename
import os


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    def sort_special(str_of_extentions: str):
        new_str_of_extentions = ''
        for item in app.config['ALLOWED_UPLOAD_EXTENSIONS']:
            if item in str_of_extentions:
                new_str_of_extentions += '  ' + item
        return new_str_of_extentions.strip()

    @app.route('/', methods=["GET", "POST"])
    def index():
        if request.method == 'POST':
            uploaded_file = request.files['file_name']
            filename = secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1][1:]
            if filename and (file_ext in app.config['ALLOWED_UPLOAD_EXTENSIONS']):
                filename_wo_ext = os.path.splitext(filename)[0]
                audir_already_in_DB = Audir_data.query.filter(Audir_data.audir_title == filename_wo_ext).first()
                if audir_already_in_DB:
                    existing_formats = audir_already_in_DB.available_formats

                if not audir_already_in_DB:
                    new_audir_for_DB = Audir_data(
                        audir_title=filename_wo_ext,
                        uploaded=dt.now(),
                        available_formats=file_ext)

                    db.session.add(new_audir_for_DB)
                    db.session.commit()
                    path_to_save = os.path.join(app.config['UPLOAD_PATH'], filename)
                    uploaded_file.save(path_to_save)

                elif (file_ext in ['jpg', 'png']) and \
                     ('jpg' in existing_formats or 'png' in existing_formats):
                    return redirect(url_for('index'))

                elif not (file_ext in existing_formats):
                    available_formats_edited = file_ext + '  ' + existing_formats
                    available_formats_sorted = sort_special(available_formats_edited)
                    audir_already_in_DB.available_formats = available_formats_sorted
                    db.session.add(audir_already_in_DB)
                    db.session.commit()
                    path_to_save = os.path.join(app.config['UPLOAD_PATH'], filename)
                    uploaded_file.save(path_to_save)

            return redirect(url_for('index'))

        audir_files = Audir_data.query

        return render_template("index.html", audir_files=audir_files)

    @app.route('/player')
    def play():
        return render_template("player.html")

    @app.errorhandler(413)
    def too_large(e):
        return "File is too large", 413

    return app
