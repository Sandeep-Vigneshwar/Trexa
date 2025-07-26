import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List, Dict, Any


def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


class EmbeddingService:
    def __init__(self):
        # Setting up GPU (cpu as fallback)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"EmbeddingService is using device: {self.device}")

        # load e5smallv2 model from huggingface
        try:
            self.tokenizer = AutoTokenizer.from_pretrained('intfloat/e5-small-v2')
            self.model = AutoModel.from_pretrained('intfloat/e5-small-v2')
            self.model.to(self.device)
            self.model.eval()
            print("Model and tokenizer loaded successfully.")
        except Exception as e:
            print(f"Error loading model or tokenizer: {e}")
            raise

    def _embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        # tokenizing batch of texts
        batch_dict = self.tokenizer(
            texts, 
            max_length=512, 
            padding=True, 
            truncation=True, 
            return_tensors='pt'
        )
        
        batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
        with torch.no_grad():
            outputs = self.model(**batch_dict)
        embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
        embeddings = F.normalize(embeddings, p=2, dim=1) # L2 normalization
        return embeddings.cpu().tolist()

    def get_embedding(self, text: str) -> List[float]:
        prefixed_text = f"query: {text}"
        embedding = self._embed([prefixed_text])[0]
        return embedding

    def get_document_embedding_chunks(self, document: str, chunk_size: int = 256) -> List[List[float]]:
        words = document.split()
        if not words:
            return []
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        prefixed_chunks = [f"passage: {chunk}" for chunk in chunks]
        embeddings = self._embed(prefixed_chunks)
        return embeddings

embedding_service = EmbeddingService()
