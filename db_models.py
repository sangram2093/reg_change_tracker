from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Regulation(db.Model):
    __tablename__ = 'regulations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    uploads = db.relationship('Upload', backref='regulation', lazy=True)

class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    regulation_id = db.Column(db.Integer, db.ForeignKey('regulations.id'), nullable=False)
    old_path = db.Column(db.String(1024), nullable=False)
    new_path = db.Column(db.String(1024), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    graph = db.relationship('Graph', uselist=False, backref='upload')
    log = db.relationship('Log', uselist=False, backref='upload')
    kop = db.relationship('KOP', uselist=False, backref='upload')

class Graph(db.Model):
    __tablename__ = 'graphs'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id'), nullable=False)
    graph_old_json = db.Column(db.Text, nullable=False)
    graph_new_json = db.Column(db.Text, nullable=False)
    diff_json = db.Column(db.Text)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id'), nullable=False)
    summary_text = db.Column(db.Text)
    raw_llm_response = db.Column(db.Text)

class KOP(db.Model):
    __tablename__ = 'kops'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.id'), nullable=False)
    kop_text = db.Column(db.Text)
    generated_time = db.Column(db.DateTime, default=datetime.utcnow)
