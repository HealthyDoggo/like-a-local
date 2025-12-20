"""Embedding service using sentence-transformers"""
import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np
from backend.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding service using sentence-transformers"""
    
    def __init__(self):
        self.model = None
        self._model_loaded = False
    
    def _load_model(self):
        """Lazy load the embedding model"""
        if self._model_loaded:
            return
        
        try:
            logger.info(f"Loading embedding model: {settings.embedding_model_name}")
            self.model = SentenceTransformer(
                settings.embedding_model_name,
                cache_folder=settings.model_cache_dir
            )
            self._model_loaded = True
            logger.info("Embedding model loaded")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        self._load_model()
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            # Convert to list of floats
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        if not texts:
            return []
        
        self._load_model()
        
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10
            )
            # Convert to list of lists of floats
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Global instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

