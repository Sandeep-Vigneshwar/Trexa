import chromadb
import logging
from typing import List, Dict, Any, Optional
from .embedding_service import EmbeddingService


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CHROMA_DATA_PATH = "./backend/data"
COLLECTION_NAME = "trexa_index"


client: Optional[chromadb.Client] = None
collection: Optional[chromadb.Collection] = None
embedding_service = EmbeddingService()


def initialize_vector_store() -> None:
    global client, collection
    
    if collection is not None:
        logging.info("Vector store is already initialized.")
        return

    try:
        client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logging.info(f"Successfully initialized ChromaDB client. Collection '{COLLECTION_NAME}' is ready.")

    except Exception as e:
        logging.error(f"Failed to initialize ChromaDB: {e}", exc_info=True)
        raise


def add_embeddings(documents: List[Dict[str, Any]]) -> None:
    if collection is None:
        raise ValueError("Vector store has not been initialized. Call initialize_vector_store() first.")
    if not documents:
        logging.warning("add_embeddings called with an empty list of documents.")
        return
    try:
        ids = [doc['id'] for doc in documents]
        embeddings = [doc['embedding'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        contents = [doc['text'] for doc in documents]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=contents
        )
        logging.info(f"Successfully added {len(ids)} documents to the '{COLLECTION_NAME}' collection.")

    except Exception as e:
        logging.error(f"Failed to add embeddings to ChromaDB: {e}", exc_info=True)
        raise


def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    if collection is None:
        raise ValueError("Vector store has not been initialized. Call initialize_vector_store() first.")

    try:
        query_embedding = embedding_service.get_embedding(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        seen_files = set()
        file_results = []
        if results and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                file_path = metadata.get('file_path')
                file_name = metadata.get('file_name')
                distance = results['distances'][0][i]
                if file_path and file_path not in seen_files:
                    seen_files.add(file_path)
                    file_results.append({
                        "file_path": file_path,
                        "file_name": file_name,
                        "score": 1 - distance
                    })
                if len(file_results) >= top_k:
                    break
        logging.info(f"Search for query '{query}' returned {len(file_results)} unique files.")
        return file_results

    except Exception as e:
        logging.error(f"Failed to perform search in ChromaDB: {e}", exc_info=True)
        raise


def clear_index() -> None:
    global collection
    
    if client is None:
        raise ValueError("Vector store has not been initialized. Call initialize_vector_store() first.")

    try:
        logging.warning(f"Attempting to delete collection: {COLLECTION_NAME}")
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logging.info(f"Successfully cleared and recreated collection '{COLLECTION_NAME}'.")
    except Exception as e:
        logging.error(f"Failed to clear collection '{COLLECTION_NAME}': {e}", exc_info=True)
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
        except Exception:
            collection = None
            logging.critical("Failed to recover collection after deletion attempt. It may be in an inconsistent state.")
        raise