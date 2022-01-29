from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime as dt
from webapp.model import db, Audir_data
from werkzeug.utils import secure_filename
import os
import re

glob_audio_current_time = 0
glob_audir_id = 1

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    def sort_special(str_of_extentions: str):
        new_str_of_extentions = ''
        for item in app.config['ALLOWED_UPLOAD_EXTENSIONS']:
            if item in str_of_extentions:
                new_str_of_extentions = new_str_of_extentions + ' ' + item
        return new_str_of_extentions.strip()

    def save_file(file_to_save, record_to_DB, uploaded_file):
        db.session.add(record_to_DB)
        db.session.commit()
        path_to_save = os.path.join(app.config['UPLOAD_PATH'], file_to_save)
        uploaded_file.save(path_to_save)

    def prepare_tagged_text(text_file_name_wo_ext):
        with open(os.path.join(app.config['UPLOAD_PATH'], text_file_name_wo_ext+".txt"), "r") as text_file:
            text = text_file.read()
        words = re.split(r"[., \-!?:_;\"“”‘’‹›«»–„\\\n\[\]\(\)]+", text)
        words_list = []
        for word in words:
            if not re.findall(r"[0-9]+", word) and len(word)>3:
                words_list.append(word)
        with open(os.path.join(app.config['UPLOAD_PATH'],text_file_name_wo_ext+".lst"), "w") as output_file:
            for word in words_list:
                output_file.write(word + '\n')


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
                    if not (file_ext in existing_formats):
                        available_formats_edited = file_ext + ' ' + existing_formats
                        available_formats_sorted = sort_special(available_formats_edited)
                        audir_already_in_DB.available_formats = available_formats_sorted
                        save_file(filename, audir_already_in_DB, uploaded_file)
                        if file_ext == 'txt':
                            prepare_tagged_text(filename_wo_ext)

                else:
                    new_audir_for_DB = Audir_data(
                    audir_title=filename_wo_ext,
                    uploaded=dt.now(),
                    available_formats=file_ext)
                    save_file(filename, new_audir_for_DB, uploaded_file)
                    if file_ext == 'txt':
                        prepare_tagged_text(filename_wo_ext)
                
            return redirect(url_for('index'))

        audir_files = Audir_data.query
        return render_template("index.html", audir_files=audir_files)

    @app.route('/<int:audir_id>')
    def play(audir_id):
        global glob_audio_current_time
        glob_audio_current_time += 1   # trial
        global glob_audir_id 
        glob_audir_id = audir_id    # trial
        #print("glob_audio_current_time:", glob_audio_current_time)
        #print("glob_audir_id:", glob_audir_id)

        audir_title = Audir_data.query.filter_by(id=audir_id).one().audir_title
        audir_exts = Audir_data.query.filter_by(id=audir_id).one().available_formats
        
        if 'jpg' in audir_exts:
            picture_ref = audir_title + '.jpg'
        else:
            picture_ref = "default_pic.jpg"
        
        mp3_ref = audir_title + ".mp3"
        
        with open(os.path.join(app.config['UPLOAD_PATH'],audir_title+'.txt'), 'r') as text_file:
            text = text_file.read()
        with open(os.path.join(app.config['UPLOAD_PATH'],audir_title+'.lst'), 'r') as list_file:
            words_list = list_file.read().split()
        
        
        tagged_text = ''
        start_ind = 0
        for list_index in range(len(words_list)):
            tagged_word = "<a href=/" + str(glob_audir_id) + "/" + str(list_index) + ">" + words_list[list_index] + "</a>"
            match = re.search(words_list[list_index], text[start_ind:])
            tagged_text += text[start_ind:start_ind+match.start(0)] + tagged_word
            start_ind += match.end(0)
        tagged_text += text[start_ind:]
        
        return render_template("player.html", titulo=audir_title, mp3_ref=mp3_ref, picture_ref=picture_ref, text=tagged_text)

    @app.errorhandler(413)
    def too_large(e):
        return "File is too large", 413

    return app
