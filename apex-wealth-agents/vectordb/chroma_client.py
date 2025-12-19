"""
Chroma VectorDB Client for semantic knowledge retrieval
Organized by namespaces for different knowledge types
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from .embedding_service import EmbeddingService, get_embedding_service


class ChromaVectorDB:
    """
    Chroma VectorDB client with namespace organization
    
    Namespaces:
    - /knowledge/general: General financial knowledge
    - /knowledge/market_insights: Market research and insights
    - /knowledge/strategies: Investment strategies
    - /knowledge/risk_profiles: Risk-based guidance
    """
    
    # Valid namespaces (ChromaDB doesn't allow slashes, so we use underscores)
    NAMESPACES = {
        "general": "knowledge_general",
        "market_insights": "knowledge_market_insights",
        "strategies": "knowledge_strategies",
        "risk_profiles": "knowledge_risk_profiles"
    }
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None,
        use_cloud: Optional[bool] = None
    ):
        """
        Initialize Chroma VectorDB client
        
        Args:
            persist_directory: Directory to persist Chroma data (default: ./vectordb_data)
            embedding_service: EmbeddingService instance (creates default if None)
            use_cloud: Whether to use ChromaDB Cloud (auto-detects from env vars if None)
        """
        # Check for ChromaDB Cloud credentials
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT")
        chroma_database = os.getenv("CHROMA_DATABASE")
        
        # Determine if we should use cloud
        if use_cloud is None:
            use_cloud = bool(chroma_api_key and chroma_tenant and chroma_database)
        
        if use_cloud:
            # Use ChromaDB Cloud
            if not chroma_api_key or not chroma_tenant or not chroma_database:
                raise ValueError(
                    "ChromaDB Cloud requires CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE environment variables"
                )
            
            # ChromaDB Cloud connection
            self.client = chromadb.HttpClient(
                host="api.trychroma.com",
                port=443,
                ssl=True,
                headers={
                    "X-Chroma-Token": chroma_api_key
                },
                tenant=chroma_tenant,
                database=chroma_database
            )
            self.is_cloud = True
        else:
            # Use local persistent client
            if persist_directory is None:
                # Store in project directory
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                persist_directory = os.path.join(base_dir, "vectordb_data")
            
            os.makedirs(persist_directory, exist_ok=True)
            
            # Temporarily prevent ChromaDB from reading .env files to avoid encoding issues
            original_env_file = os.environ.get('CHROMA_ENV_FILE')
            if 'CHROMA_ENV_FILE' in os.environ:
                del os.environ['CHROMA_ENV_FILE']
            
            try:
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            finally:
                # Restore original env file setting if it existed
                if original_env_file:
                    os.environ['CHROMA_ENV_FILE'] = original_env_file
            
            self.is_cloud = False
        
        # Initialize embedding service
        self.embedding_service = embedding_service or get_embedding_service()
        
        # Initialize collections for each namespace
        self.collections: Dict[str, chromadb.Collection] = {}
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize or get collections for each namespace"""
        for key, namespace in self.NAMESPACES.items():
            try:
                # Try to get existing collection
                collection = self.client.get_collection(
                    name=namespace,
                    embedding_function=None  # We'll handle embeddings manually
                )
            except Exception:
                # Create new collection if it doesn't exist
                collection = self.client.create_collection(
                    name=namespace,
                    metadata={"namespace": namespace, "type": "knowledge"}
                )
            
            self.collections[key] = collection
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        namespace: str = "general",
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to a namespace
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dicts (one per document)
            namespace: Namespace key (general, market_insights, strategies, risk_profiles)
            ids: Optional list of document IDs (auto-generated if None)
            
        Returns:
            List of document IDs
        """
        if namespace not in self.NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}. Valid: {list(self.NAMESPACES.keys())}")
        
        collection = self.collections[namespace]
        
        # Generate embeddings
        embeddings = self.embedding_service.embed(documents)
        
        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Prepare metadatas
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def search(
        self,
        query: str,
        namespace: Optional[str] = None,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity
        
        Args:
            query: Query text
            namespace: Namespace to search (searches all if None)
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of result dicts with keys: document, metadata, distance, id
        """
        # Embed query
        query_embedding = self.embedding_service.embed_single(query)
        
        results = []
        
        # Search in specified namespace or all namespaces
        namespaces_to_search = [namespace] if namespace else list(self.NAMESPACES.keys())
        
        for ns_key in namespaces_to_search:
            if ns_key not in self.collections:
                continue
            
            collection = self.collections[ns_key]
            
            # Perform search
            search_results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Format results
            if search_results.get("documents") and search_results["documents"][0]:
                for i, doc in enumerate(search_results["documents"][0]):
                    results.append({
                        "document": doc,
                        "metadata": search_results.get("metadatas", [[]])[0][i] if search_results.get("metadatas") else {},
                        "distance": search_results.get("distances", [[]])[0][i] if search_results.get("distances") else None,
                        "id": search_results.get("ids", [[]])[0][i] if search_results.get("ids") else None,
                        "namespace": ns_key
                    })
        
        # Sort by distance (lower is better) and return top_k
        results.sort(key=lambda x: x.get("distance", float('inf')))
        return results[:top_k]
    
    def delete_namespace(self, namespace: str):
        """Delete all documents in a namespace"""
        if namespace not in self.NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}")
        
        collection = self.collections[namespace]
        collection.delete()
        
        # Recreate empty collection
        namespace_name = self.NAMESPACES[namespace]
        self.collections[namespace] = self.client.create_collection(
            name=namespace_name,
            metadata={"namespace": namespace_name, "type": "knowledge"}
        )
    
    def get_collection_info(self, namespace: str) -> Dict[str, Any]:
        """Get information about a collection"""
        if namespace not in self.collections:
            return {"error": f"Namespace {namespace} not found"}
        
        collection = self.collections[namespace]
        count = collection.count()
        
        return {
            "namespace": namespace,
            "full_name": self.NAMESPACES[namespace],
            "document_count": count
        }


# Default instance
_default_vectordb = None

def get_vectordb() -> ChromaVectorDB:
    """Get or create default VectorDB instance"""
    global _default_vectordb
    if _default_vectordb is None:
        # Auto-detect cloud vs local based on environment variables
        _default_vectordb = ChromaVectorDB()
    return _default_vectordb

