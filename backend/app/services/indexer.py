import os
import logging
from typing import List, Dict, Any, Set
from . import vector_store
from .file_parser import parse_file
from .embedding_service import embedding_service

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def _index_single_file(file_path: str) -> bool:
    try:
        # parsing executes
        logging.info(f"Parsing file: {file_path}")
        text, metadata = parse_file(file_path)
        if not text or not text.strip():
            logging.warning(f"No text content extracted from {file_path}. Skipping.")
            return False

        # The embedding service handles the chunking logic.
        logging.info(f"Generating embeddings for {file_path}...")
        embeddings = embedding_service.get_document_embedding_chunks(text)
        if not embeddings:
            logging.warning(f"Could not generate embeddings for {file_path}. Skipping.")
            return False
            
        # re-creating the chunks for text
        words = text.split()
        chunk_size = 256 
        text_chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        # ensuring there are same number of text chunks as embeddings
        if len(text_chunks) != len(embeddings):
            logging.error(f"Mismatch between text chunks ({len(text_chunks)}) and embeddings ({len(embeddings)}) for {file_path}. Skipping.")
            return False

        # preparing documents for ChromaDB
        documents_to_add = []
        for i, (embedding, chunk_text) in enumerate(zip(embeddings, text_chunks)):
            chunk_id = f"{file_path}::{i}"
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "file_path": file_path,
                "file_name": os.path.basename(file_path)
            })

            documents_to_add.append({
                "id": chunk_id,
                "embedding": embedding,
                "metadata": chunk_metadata,
                "text": chunk_text
            })

        # add documents to the vector store
        if documents_to_add:
            vector_store.add_embeddings(documents_to_add)
            logging.info(f"Successfully indexed {len(documents_to_add)} chunks for {file_path}.")
        return True

    except Exception as e:
        logging.error(f"Failed to index file {file_path}: {e}", exc_info=True)
        return False


def index_directory(path: str) -> None:
    from . import vector_store
    vector_store.initialize_vector_store()
    if not os.path.isdir(path):
        logging.error(f"Provided path '{path}' is not a valid directory.")
        return

    logging.info(f"Starting to index directory: {path}")
    for root, _, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                file_path = os.path.join(root, file)
                _index_single_file(file_path)
    logging.info(f"Finished indexing directory: {path}")


def reindex_file(file_path: str) -> None:
    if not os.path.isfile(file_path):
        logging.error(f"File not found for re-indexing: {file_path}")
        return
        
    logging.info(f"Re-indexing file: {file_path}")
    delete_file_from_index(file_path)
    _index_single_file(file_path)


def delete_file_from_index(file_path: str) -> None:
    if vector_store.collection is None:
        logging.error("Cannot delete: Vector store is not initialized.")
        return
        
    try:
        logging.info(f"Deleting file from index: {file_path}")
        vector_store.collection.delete(where={"file_path": file_path})
        logging.info(f"Successfully removed all chunks for {file_path} from the index.")
    except Exception as e:
        logging.error(f"Failed to delete {file_path} from index: {e}", exc_info=True)


def status() -> Dict[str, int]:
    if vector_store.collection is None:
        logging.error("Cannot get status: Vector store is not initialized.")
        return {"total_chunks": 0, "total_files": 0}

    try:
        total_chunks = vector_store.collection.count()
        if total_chunks == 0:
            return {"total_chunks": 0, "total_files": 0}
            
        all_metadata = vector_store.collection.get(include=["metadatas"])["metadatas"]
        unique_files: Set[str] = {meta['file_path'] for meta in all_metadata if 'file_path' in meta}
        
        return {
            "total_chunks": total_chunks,
            "total_files": len(unique_files)
        }
    except Exception as e:
        logging.error(f"Failed to retrieve index status: {e}", exc_info=True)
        return {"total_chunks": -1, "total_files": -1}
