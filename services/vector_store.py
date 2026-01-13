"""
Vector Store for semantic search capabilities
"""
from typing import List, Dict, Any, Optional
import os
import json
from config import settings


class VectorStore:
    """Vector store for semantic search of resumes and job descriptions"""
    
    def __init__(self):
        self.store_path = settings.VECTOR_STORE_PATH
        self.embeddings_cache = {}
        self._ensure_store_exists()
    
    def _ensure_store_exists(self):
        """Ensure vector store directory exists"""
        os.makedirs(self.store_path, exist_ok=True)
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add document to vector store"""
        
        # In production, use proper vector DB like ChromaDB or FAISS
        # This is a simple file-based implementation
        
        doc_data = {
            'id': doc_id,
            'text': text,
            'metadata': metadata or {},
            'embedding': self._generate_embedding(text)
        }
        
        doc_path = os.path.join(self.store_path, f"{doc_id}.json")
        
        with open(doc_path, 'w') as f:
            json.dump(doc_data, f)
        
        self.embeddings_cache[doc_id] = doc_data['embedding']
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        
        query_embedding = self._generate_embedding(query)
        
        # Load all documents
        results = []
        
        for filename in os.listdir(self.store_path):
            if not filename.endswith('.json'):
                continue
            
            doc_path = os.path.join(self.store_path, filename)
            
            with open(doc_path, 'r') as f:
                doc_data = json.load(f)
            
            # Apply metadata filters
            if filter_metadata:
                match = all(
                    doc_data['metadata'].get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue
            
            # Calculate similarity
            similarity = self._cosine_similarity(
                query_embedding,
                doc_data['embedding']
            )
            
            results.append({
                'id': doc_data['id'],
                'text': doc_data['text'],
                'metadata': doc_data['metadata'],
                'similarity_score': similarity
            })
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def search_candidates_by_skills(
        self,
        required_skills: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for candidates matching required skills"""
        
        query = f"Candidate with skills: {', '.join(required_skills)}"
        
        return self.search(
            query,
            top_k=top_k,
            filter_metadata={'type': 'resume'}
        )
    
    def search_similar_jobs(
        self,
        job_description: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar job postings"""
        
        return self.search(
            job_description,
            top_k=top_k,
            filter_metadata={'type': 'job'}
        )
    
    def delete_document(self, doc_id: str):
        """Remove document from vector store"""
        
        doc_path = os.path.join(self.store_path, f"{doc_id}.json")
        
        if os.path.exists(doc_path):
            os.remove(doc_path)
        
        if doc_id in self.embeddings_cache:
            del self.embeddings_cache[doc_id]
    
    def update_document(
        self,
        doc_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update existing document"""
        
        doc_path = os.path.join(self.store_path, f"{doc_id}.json")
        
        if not os.path.exists(doc_path):
            raise ValueError(f"Document {doc_id} not found")
        
        with open(doc_path, 'r') as f:
            doc_data = json.load(f)
        
        if text:
            doc_data['text'] = text
            doc_data['embedding'] = self._generate_embedding(text)
        
        if metadata:
            doc_data['metadata'].update(metadata)
        
        with open(doc_path, 'w') as f:
            json.dump(doc_data, f)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document by ID"""
        
        doc_path = os.path.join(self.store_path, f"{doc_id}.json")
        
        if not os.path.exists(doc_path):
            return None
        
        with open(doc_path, 'r') as f:
            return json.load(f)
    
    def list_documents(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List all documents"""
        
        documents = []
        
        for filename in os.listdir(self.store_path):
            if not filename.endswith('.json'):
                continue
            
            doc_path = os.path.join(self.store_path, filename)
            
            with open(doc_path, 'r') as f:
                doc_data = json.load(f)
            
            # Apply filters
            if filter_metadata:
                match = all(
                    doc_data['metadata'].get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue
            
            documents.append({
                'id': doc_data['id'],
                'metadata': doc_data['metadata']
            })
        
        return documents
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (simplified)"""
        
        # In production, use sentence-transformers or OpenAI embeddings
        # This is a mock implementation using simple hashing
        
        import hashlib
        
        # Create a deterministic "embedding" from text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to list of floats (384 dimensions)
        embedding = []
        for i in range(0, len(hash_bytes), 2):
            val = (hash_bytes[i] + hash_bytes[i+1] * 256) / 65535.0
            embedding.append(val)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """Calculate cosine similarity between two vectors"""
        
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same length")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def clear_store(self):
        """Clear all documents from store"""
        
        for filename in os.listdir(self.store_path):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.store_path, filename))
        
        self.embeddings_cache.clear()


# Global vector store instance
vector_store = VectorStore()