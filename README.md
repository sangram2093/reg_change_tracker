# Regulatory Graph Comparison & KOP Generation Platform

A web-based application that enables regulatory analysts and operations teams to upload, compare, and approve regulatory documents. It extracts entity relationships using LLM (Gemini/Vertex AI), constructs directed graphs, detects differences between regulatory versions, and generates Key Operating Procedures (KOP) in Word format.

---

## 🔍 Features

- **PDF Upload (First-time & Comparison Mode)**: Upload new or updated regulation PDFs.
- **LLM Integration**: Uses Vertex AI/Gemini for contextual summarization and entity relationship extraction.
- **Graph Visualization**: Interactive graph rendering using Vis.js to depict regulatory relationships.
- **Graph Comparison**: Highlights added/changed edges between old and new regulations.
- **KOP Generation**: One-click generation of Word-based KOP documents from regulatory summaries and graphs.
- **Audit Trail**: Stores all uploads, summaries, graphs, and history for compliance and traceability.
- **Responsive UI**: Clean and user-friendly HTML interface for regulatory analysis workflows.

---

## 📁 Project Structure

```
project-root/
│
├── app.py                     # Main Flask application
├── db_models.py              # SQLAlchemy ORM models for PostgreSQL
├── utils.py                  # PDF text extraction, graph parsing & comparison
├── vertex_llm.py             # LLM invocation for summarization and relationship extraction
│
├── templates/
│   ├── index.html            # Upload page
│   ├── compare.html          # Graph comparison and KOP generation screen
│   └── history.html          # History log of uploads
│
├── static/                   # JS, CSS, and assets
├── requirements.txt          # Python dependencies
└── README.md                 # You're here!
```

---

## 🧪 Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **LLM**: Google Vertex AI / Gemini
- **Graph Engine**: NetworkX
- **Frontend**: HTML5, JavaScript (Vis.js, html2canvas)
- **Document Generation**: `python-docx`

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/regulation-graph-kop.git
cd regulation-graph-kop
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Database

Update `app.py` with your PostgreSQL credentials:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://<username>:<password>@<host>:<port>/<dbname>'
```

Initialize DB tables:

```bash
python
>>> from app import db, app
>>> with app.app_context():
...     db.create_all()
...
```

### 4. Configure Vertex AI

Set your GCP environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### 5. Run the Application

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🧠 How It Works

1. **Upload PDFs**: Choose regulation and upload new or both old/new PDFs.
2. **LLM Analysis**: Summarizes content, extracts entities & relationships.
3. **Graph Rendering**: Builds interactive directed graphs with tooltips.
4. **Comparison Logic**: Highlights modified or newly added edges.
5. **KOP Generation**: Uses LLM to generate operational steps as a Word doc.

---

## 📦 Dependencies

- Flask
- SQLAlchemy
- psycopg2-binary
- python-docx
- fitz (PyMuPDF)
- networkx
- google-cloud-aiplatform
- html2canvas (JS)

Install them using:

```bash
pip install -r requirements.txt
```

---

## 📝 License

This project is licensed under the MIT License. See `LICENSE` for more details.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for enhancements or bug fixes.

---

## 📧 Contact

For support or questions, please contact:

- Team Aura
