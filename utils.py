import fitz  # PyMuPDF
import json
import networkx as nx
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
            f"Frequency: {rel.get('frequency', '')}"
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

def generate_kop(old_summary, new_summary, old_json_str, new_json_str, output_path):
    packet = BytesIO()
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    def draw_section(title, content, start_y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, start_y, title)
        c.setFont("Helvetica", 10)
        lines = content.split("\n")
        y = start_y - 15
        for line in lines:
            for wrapped in split_line(line, 100):
                if y < 40:
                    c.showPage()
                    y = height - 40
                    c.setFont("Helvetica", 10)
                c.drawString(40, y, wrapped)
                y -= 14
        return y - 20

    def split_line(line, max_chars=100):
        return [line[i:i+max_chars] for i in range(0, len(line), max_chars)]

    y = height - 40
    y = draw_section("Old Regulation Summary", old_summary, y)
    y = draw_section("New Regulation Summary", new_summary, y)

    old_json = json.loads(old_json_str)
    new_json = json.loads(new_json_str)

    y = draw_section("Old Entity Relationships", json.dumps(old_json, indent=2), y)
    y = draw_section("New Entity Relationships", json.dumps(new_json, indent=2), y)

    c.save()
