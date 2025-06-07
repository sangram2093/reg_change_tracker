import fitz  # PyMuPDF
import json
import networkx as nx


def extract_text_from_pdf(path):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def parse_graph_data(relationship_json):
    """
    Converts entity relationship JSON into a NetworkX DiGraph.
    Each edge has properties that will be used in tooltips (title in vis.js).
    """
    if isinstance(relationship_json, str):
        relationship_json = json.loads(relationship_json)

    G = nx.DiGraph()

    # Add nodes
    for entity in relationship_json.get("entities", []):
        G.add_node(entity["id"], label=entity["name"], group=entity["type"])

    # Add edges with detailed relationship information in the tooltip
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
    """
    Compares two graphs (old and new) and returns sets of:
    - changed_edges: edges whose label or title differs
    - added_nodes: new nodes in G_new
    - removed_nodes: nodes that were removed
    """
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


def generate_kop(summary_text):
    header = "Key Operating Procedure (KOP) Document\n\n"
    intro = "This KOP document is generated based on the approved changes extracted from regulation text.\n\n"
    return header + intro + summary_text
