"""
Knowledge Store for managing financial knowledge documents
Handles chunking, storage, and retrieval of knowledge content
"""
import re
from typing import List, Dict, Any, Optional
from .chroma_client import ChromaVectorDB, get_vectordb
from .embedding_service import EmbeddingService


class KnowledgeStore:
    """
    Manages storage and retrieval of financial knowledge
    
    Handles:
    - Document chunking (300-800 tokens)
    - Metadata management
    - Namespace organization
    """
    
    # Approximate tokens per character (for English text)
    CHARS_PER_TOKEN = 4
    
    def __init__(self, vectordb: Optional[ChromaVectorDB] = None):
        """
        Initialize Knowledge Store
        
        Args:
            vectordb: ChromaVectorDB instance (creates default if None)
        """
        self.vectordb = vectordb or get_vectordb()
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into segments of approximately 300-800 tokens
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens (default 500, range 300-800)
            chunk_overlap: Overlap between chunks in tokens (default 50)
            
        Returns:
            List of chunk dicts with keys: text, start_pos, end_pos, chunk_index
        """
        # Validate chunk size
        if chunk_size < 300:
            chunk_size = 300
        elif chunk_size > 800:
            chunk_size = 800
        
        # Convert tokens to characters (approximate)
        chunk_chars = chunk_size * self.CHARS_PER_TOKEN
        overlap_chars = chunk_overlap * self.CHARS_PER_TOKEN
        
        chunks = []
        start = 0
        chunk_index = 0
        
        # Split by paragraphs first for better semantic boundaries
        paragraphs = re.split(r'\n\s*\n', text)
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would exceed chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > chunk_chars:
                chunks.append({
                    "text": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "start_pos": start,
                    "end_pos": start + len(current_chunk)
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                current_chunk = overlap_text + "\n\n" + para
                start = start + len(current_chunk) - len(overlap_text) - len(para)
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                    start = 0  # Track position in original text
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "start_pos": start,
                "end_pos": start + len(current_chunk)
            })
        
        return chunks
    
    def store_document(
        self,
        content: str,
        title: str,
        namespace: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> List[str]:
        """
        Store a document in VectorDB with automatic chunking
        
        Args:
            content: Document content
            title: Document title
            namespace: Namespace (general, market_insights, strategies, risk_profiles)
            metadata: Additional metadata
            source: Source of the document (URL, file path, etc.)
            
        Returns:
            List of chunk IDs
        """
        # Chunk the document
        chunks = self.chunk_text(content)
        
        # Prepare documents and metadatas
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{title}_{i}_{hash(chunk['text']) % 10000}"
            ids.append(chunk_id)
            documents.append(chunk['text'])
            
            chunk_metadata = {
                "title": title,
                "chunk_index": chunk['chunk_index'],
                "total_chunks": len(chunks),
                "source": source or "unknown"
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            metadatas.append(chunk_metadata)
        
        # Store in VectorDB
        return self.vectordb.add_documents(
            documents=documents,
            metadatas=metadatas,
            namespace=namespace,
            ids=ids
        )
    
    def retrieve_knowledge(
        self,
        query: str,
        namespace: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge chunks for a query
        
        Args:
            query: User query
            namespace: Specific namespace to search (searches all if None)
            top_k: Number of results to return
            
        Returns:
            List of knowledge chunks with metadata
        """
        results = self.vectordb.search(
            query=query,
            namespace=namespace,
            top_k=top_k
        )
        
        # Format results with additional context
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result["document"],
                "metadata": result["metadata"],
                "relevance_score": 1.0 - result.get("distance", 1.0),  # Convert distance to similarity
                "namespace": result.get("namespace", "unknown"),
                "id": result.get("id")
            })
        
        return formatted_results
    
    def store_market_insight(
        self,
        content: str,
        title: str,
        date: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[str]:
        """Store market research/insight document"""
        metadata = {"type": "market_insight", "date": date} if date else {"type": "market_insight"}
        return self.store_document(
            content=content,
            title=title,
            namespace="market_insights",
            metadata=metadata,
            source=source
        )
    
    def store_strategy(
        self,
        content: str,
        title: str,
        strategy_type: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[str]:
        """Store investment strategy document"""
        metadata = {}
        if strategy_type:
            metadata["strategy_type"] = strategy_type
        if risk_level:
            metadata["risk_level"] = risk_level
        metadata["type"] = "strategy"
        
        return self.store_document(
            content=content,
            title=title,
            namespace="strategies",
            metadata=metadata,
            source=None
        )
    
    def store_risk_guidance(
        self,
        content: str,
        title: str,
        risk_profile: str
    ) -> List[str]:
        """Store risk-profile-based guidance"""
        return self.store_document(
            content=content,
            title=title,
            namespace="risk_profiles",
            metadata={"type": "risk_guidance", "risk_profile": risk_profile},
            source=None
        )


# Default instance
_default_knowledge_store = None

def get_knowledge_store() -> KnowledgeStore:
    """Get or create default Knowledge Store instance"""
    global _default_knowledge_store
    if _default_knowledge_store is None:
        _default_knowledge_store = KnowledgeStore()
    return _default_knowledge_store

