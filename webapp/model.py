from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Audir_data(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        audir_title = db.Column(db.String, nullable=False)
        uploaded = db.Column(db.DateTime, nullable=False)
        available_formats = db.Column(db.String, unique=True, nullable=False)
    
        def __repr__(self):
            return '<Audir material: {} {}>'.format(self.audir_title, self.available_formats)