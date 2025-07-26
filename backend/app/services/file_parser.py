import os
import re
import fitz
import docx
from typing import Tuple, Dict, Any
from datetime import datetime

def parse_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File not found at '{file_path}'")

    text = ""
    metadata = {}
    
    try:
        file_stat = os.stat(file_path)
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_path': os.path.abspath(file_path),
            'file_size_bytes': file_stat.st_size,
            'last_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        }
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            with fitz.open(file_path) as doc:
                text = "".join(page.get_text() for page in doc)
                bullet_pattern = r'[\u2022\u25CF\u25CB\u25AA]\s*'
                text = re.sub(bullet_pattern, '', text)
                pdf_metadata = doc.metadata
                metadata.update({
                    'pdf_author': pdf_metadata.get('author'),
                    'pdf_title': pdf_metadata.get('title'),
                    'pdf_creation_date': pdf_metadata.get('creationDate'),
                    'page_count': doc.page_count,
                })
        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            text = re.sub(r'\n+', '\n', text)
            text = text.strip()
            core_properties = doc.core_properties
            metadata.update({
                'docx_author': core_properties.author,
                'docx_created': core_properties.created.isoformat() if core_properties.created else None,
                'docx_title': core_properties.title,
            })
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: '{file_extension}'. Only .pdf, .docx, and .txt are supported.")

    except Exception as e:
        print(f"An error occurred while processing '{file_path}': {e}")
        return "", metadata

    return text, metadata
