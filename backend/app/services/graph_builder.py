import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

# configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
OUTPUT_DIR = "data"
OUTPUT_FILENAME = "file_tree_graph.json"

# style configuration
FOLDER_COLOR = "rgba(93, 109, 126, 0.8)"  # Grey
FILE_COLOR = "rgba(52, 152, 219, 0.8)"    # Blue

def build_file_tree_graph(root_path: str) -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.isdir(root_path):
        logging.error(f"Provided path '{root_path}' is not a valid directory.")
        return {"nodes": [], "links": []}

    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    root_name = os.path.basename(os.path.abspath(root_path))
    nodes.append({
        "id": root_path,
        "label": root_name,
        "type": "folder",
        "color": FOLDER_COLOR
    })

    logging.info(f"Starting file tree scan at: {root_path}")

    for dir_path, dir_names, file_names in os.walk(root_path, topdown=True):
        # Filter out hidden directories from further traversal
        dir_names[:] = [d for d in dir_names if not d.startswith('.')]
        # Filter out hidden files
        file_names = [f for f in file_names if not f.startswith('.')]

        for dir_name in dir_names:
            child_path = os.path.join(dir_path, dir_name)
            nodes.append({
                "id": child_path,
                "label": dir_name,
                "type": "folder",
                "color": FOLDER_COLOR
            })
            links.append({
                "source": dir_path,
                "target": child_path,
                "relationship": "contains"
            })

        for file_name in file_names:
            child_path = os.path.join(dir_path, file_name)
            try:
                stat = os.stat(child_path)
                size_kb = round(stat.st_size / 1024, 2)
                modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                nodes.append({
                    "id": child_path,
                    "label": file_name,
                    "type": "file",
                    "color": FILE_COLOR,
                    "size": size_kb,
                    "timestamp": modified_time
                })
                links.append({
                    "source": dir_path,
                    "target": child_path,
                    "relationship": "contains"
                })

            except (PermissionError, FileNotFoundError) as e:
                logging.warning(f"Could not access metadata for {child_path}: {e}")
                continue

    graph_data = {"nodes": nodes, "links": links}
    logging.info(f"Graph built successfully: {len(nodes)} nodes and {len(links)} links created.")

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
        logging.info(f"Successfully wrote graph data to {output_path}")
    except IOError as e:
        logging.error(f"Failed to write graph data to file: {e}")

    return graph_data
