import fitz
import networkx as nx
import json

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

def parse_graph_data(data):
    G = nx.DiGraph()
    for entity in data.get("entities", []):
        G.add_node(entity["id"], label=entity["name"], group=entity.get("type", "Entity"))

    for rel in data.get("relationships", []):
        G.add_edge(
            rel["subject_id"],
            rel["object_id"],
            label=rel.get("verb", "relates"),
            title=f"Confidence: {rel.get('confidence_score', 'N/A')}"
        )
    return G

def compare_graphs(G_old, G_new):
    node_diff = {
        "added": list(set(G_new.nodes()) - set(G_old.nodes())),
        "removed": list(set(G_old.nodes()) - set(G_new.nodes()))
    }
    edge_diff = {
        "added": list(set(G_new.edges()) - set(G_old.edges())),
        "removed": list(set(G_old.edges()) - set(G_new.edges()))
    }
    return {"nodes": node_diff, "edges": edge_diff}

def generate_kop(summary_text):
    header = "Key Operating Procedure (KOP) Document\n\n"
    intro = "This KOP document is generated based on the approved changes extracted from regulation text.\n\n"
    return header + intro + summary_text
