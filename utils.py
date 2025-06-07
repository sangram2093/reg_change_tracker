import fitz  # PyMuPDF
import json
import networkx as nx
from fpdf import FPDF

def extract_text_from_pdf(path):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_graph_data(relationship_json):
    """Parses entity relationship JSON into NetworkX DiGraph with vis.js-compatible properties."""
    if isinstance(relationship_json, str):
        relationship_json = json.loads(relationship_json)

    G = nx.DiGraph()

    for entity in relationship_json.get("entities", []):
        G.add_node(entity["id"], label=entity["name"], group=entity["type"])

    for rel in relationship_json.get("relationships", []):
        tooltip_lines = [
            f"Verb: {rel.get('verb', '')}",
            f"Optionality: {rel.get('Optionality', '')}",
            f"Condition: {rel.get('Condition for Relationship to be Active', '')}",
            f"Property: {rel.get('Property of Object (part of condition)', '')}",
            f"Thresholds: {rel.get('Thresholds', '')}",
            f"Frequency: {rel.get('frequence', '')}"
        ]
        tooltip_text = "\n".join(tooltip_lines)

        G.add_edge(
            rel["subject_id"],
            rel["object_id"],
            label=rel.get("verb", ""),
            title=tooltip_text
        )

    return G

def compare_graphs(G_old, G_new):
    """Compares old and new graphs to identify changed edges and nodes."""
    changed_edges = []
    added_nodes = list(set(G_new.nodes) - set(G_old.nodes))
    removed_nodes = list(set(G_old.nodes) - set(G_new.nodes))

    for u, v in G_new.edges:
        if G_old.has_edge(u, v):
            old_data = G_old[u][v]
            new_data = G_new[u][v]
            if old_data.get("label") != new_data.get("label") or old_data.get("title") != new_data.get("title"):
                changed_edges.append((u, v))
        else:
            changed_edges.append((u, v))

    return changed_edges, added_nodes, removed_nodes

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", size=12)
        self.cell(0, 10, "Knowledge of Process (KOP) Document", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_kop(summary_old, summary_new, entity_json_old, entity_json_new):
    """Generates a Unicode-compliant PDF containing summaries and relationships."""
    pdf = PDF()
    pdf.add_page()

    # Load Unicode-compatible font
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)

    pdf.multi_cell(0, 10, "=== Old Summary ===")
    pdf.multi_cell(0, 10, summary_old)
    pdf.ln(10)

    pdf.multi_cell(0, 10, "=== New Summary ===")
    pdf.multi_cell(0, 10, summary_new)
    pdf.ln(10)

    pdf.multi_cell(0, 10, "=== Old Entity Relationship ===")
    pdf.multi_cell(0, 10, json.dumps(json.loads(entity_json_old), indent=2))
    pdf.ln(10)

    pdf.multi_cell(0, 10, "=== New Entity Relationship ===")
    pdf.multi_cell(0, 10, json.dumps(json.loads(entity_json_new), indent=2))

    file_path = "KOP_Document.pdf"
    pdf.output(file_path)
    return file_path
