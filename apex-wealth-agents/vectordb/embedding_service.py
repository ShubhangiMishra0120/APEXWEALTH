"""
Embedding Service for converting text to embeddings
Supports OpenAI text-embedding-3-large and local models
"""
import os
import requests
from typing import List, Optional
import numpy as np

# Note: We use local embeddings (sentence-transformers) by default
# OpenAI embeddings are optional and only used if explicitly configured


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self, model: str = "text-embedding-3-large", api_key: Optional[str] = None):
        """
        Initialize embedding service
        
        Args:
            model: Embedding model name. Options:
                  - "text-embedding-3-large" (OpenAI, default)
                  - "text-embedding-3-small" (OpenAI)
                  - "local" (for local models like sentence-transformers)
            api_key: API key for OpenAI (if using OpenAI models)
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.local_model = None
        
        # Initialize local model if needed
        if model == "local":
            try:
                from sentence_transformers import SentenceTransformer
                # Use a good default local model
                self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if not texts:
            return []
        
        if self.model == "local" and self.local_model:
            # Use local model
            embeddings = self.local_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        
        # Use OpenAI API
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required for OpenAI embeddings. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        return self._embed_openai(texts)
    
    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenAI API accepts up to 2048 texts per request
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            data = {
                "model": self.model,
                "input": batch
            }
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                # Extract embeddings in the same order as input
                batch_embeddings = [item["embedding"] for item in result["data"]]
                all_embeddings.extend(batch_embeddings)
                
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to get embeddings from OpenAI: {e}")
        
        return all_embeddings
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return self.embed([text])[0]


# Default instance
_default_embedding_service = None

def get_embedding_service(model: Optional[str] = None) -> EmbeddingService:
    """Get or create default embedding service instance"""
    global _default_embedding_service
    
    if _default_embedding_service is None:
        # Default to local embeddings (sentence-transformers) since we're using FreeLLM
        # Only use OpenAI if explicitly requested and API key is available
        use_local = model != "openai" and not os.getenv("OPENAI_API_KEY")
        
        if use_local:
            try:
                _default_embedding_service = EmbeddingService(model="local")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )
        else:
            # Use OpenAI only if explicitly requested
            _default_embedding_service = EmbeddingService(
                model=model or "text-embedding-3-large"
            )
    
    return _default_embedding_service

