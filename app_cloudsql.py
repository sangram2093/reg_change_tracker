import os
from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from vertex_llm import init_vertexai, get_summary_entities
from utils import extract_text_from_pdf, parse_graph_data, compare_graphs, generate_kop
from db_models import db, Regulation, Upload, Graph, Log, KOP
import json
import networkx as nx

# Cloud SQL PostgreSQL via pg8000
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy

# Configuration for Cloud SQL
INSTANCE_CONNECTION_NAME = "db-abc-t4fr-fra-001-1:europe-west13:cdfra-dev-postgresql01"
DB_USER = "db_admin"
DB_PASS = "pwd"
DB_NAME = "postgres"
ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PRIVATE

connector = Connector(ip_type)

def getconn():
    return connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )

engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploaded_docs"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("kop_docs", exist_ok=True)

db.init_app(app)

init_vertexai()

@app.before_first_request
def initialize_database():
    with app.app_context():
        db.create_all(bind=engine)

@app.route("/", methods=["GET", "POST"])
def index():
    regulations = Regulation.query.all()
    if request.method == "POST":
        regulation_id = request.form['regulation']
        old_file = request.files['old_pdf']
        new_file = request.files['new_pdf']
        old_filename = secure_filename(old_file.filename)
        new_filename = secure_filename(new_file.filename)
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
        new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        old_file.save(old_path)
        new_file.save(new_path)
        upload = Upload(regulation_id=regulation_id, old_path=old_path, new_path=new_path)
        db.session.add(upload)
        db.session.commit()
        return redirect(url_for('compare', upload_id=upload.id))
    return render_template("index.html", regulations=regulations)

@app.route("/compare/<int:upload_id>")
def compare(upload_id):
    return render_template("compare.html", upload_id=upload_id)

@app.route("/graph_data/<int:upload_id>/<version>")
def graph_data(upload_id, version):
    graph_entry = Graph.query.filter_by(upload_id=upload_id).first()
    if not graph_entry:
        upload = Upload.query.get(upload_id)
        text = extract_text_from_pdf(upload.old_path if version == "old" else upload.new_path)
        json_str = get_summary_entities(text, version)
        data = json.loads(json_str)
        G = parse_graph_data(data)
        graph_json = json.dumps({
            "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes],
            "edges": [{"from": u, "to": v, **G[u][v]} for u, v in G.edges]
        })
        new_graph = Graph(upload_id=upload_id,
                          graph_old_json=graph_json if version == "old" else "",
                          graph_new_json=graph_json if version == "new" else "")
        db.session.add(new_graph)
        db.session.add(Log(upload_id=upload_id, summary_text=text, raw_llm_response=json_str))
        db.session.commit()
    else:
        graph_json = graph_entry.graph_old_json if version == "old" else graph_entry.graph_new_json
    return jsonify(json.loads(graph_json))

@app.route("/regenerate/<int:upload_id>")
def regenerate(upload_id):
    Graph.query.filter_by(upload_id=upload_id).delete()
    db.session.commit()
    return redirect(url_for("compare", upload_id=upload_id))

@app.route("/approve/<int:upload_id>")
def approve(upload_id):
    logs = Log.query.filter_by(upload_id=upload_id).first()
    summary = logs.summary_text if logs else ""
    kop_text = generate_kop(summary)
    kop_path = f"kop_docs/kop_{upload_id}.txt"
    with open(kop_path, "w") as f:
        f.write(kop_text)
    db.session.add(KOP(upload_id=upload_id, kop_text=kop_text, path=kop_path))
    db.session.commit()
    return send_file(kop_path, as_attachment=True)

@app.route("/history")
def history():
    uploads = Upload.query.order_by(Upload.upload_time.desc()).all()
    return render_template("history.html", uploads=uploads)

if __name__ == "__main__":
    app.run(debug=True)
