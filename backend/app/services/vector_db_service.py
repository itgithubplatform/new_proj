"""Vector Database Service using ChromaDB for conversation context storage"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import json
import uuid


class VectorDBService:
    """Service for managing conversation context using ChromaDB"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "TalentScout conversation context storage"}
        )
    
    def store_conversation_context(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        candidate_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store conversation context in vector DB
        
        Args:
            conversation_id: Unique conversation identifier
            messages: List of conversation messages
            candidate_data: Current candidate information
        """
        # Create context document
        context_text = self._create_context_text(messages, candidate_data)
        
        # Store in ChromaDB
        self.collection.add(
            documents=[context_text],
            metadatas=[{
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "has_candidate_data": bool(candidate_data)
            }],
            ids=[f"{conversation_id}_ctx_{uuid.uuid4()}"]
        )
    
    def get_conversation_context(
        self,
        conversation_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation context from vector DB
        
        Args:
            conversation_id: Unique conversation identifier
            limit: Number of context items to retrieve
            
        Returns:
            List of relevant context items
        """
        results = self.collection.query(
            query_texts=[conversation_id],
            where={"conversation_id": conversation_id},
            n_results=limit
        )
        
        return results
    
    def search_similar_conversations(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar conversations based on query
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of similar conversation contexts
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        return results
    
    def delete_conversation_context(self, conversation_id: str) -> None:
        """Delete all context for a conversation
        
        Args:
            conversation_id: Unique conversation identifier
        """
        # Get all IDs for this conversation
        results = self.collection.get(
            where={"conversation_id": conversation_id}
        )
        
        if results and results['ids']:
            self.collection.delete(ids=results['ids'])
    
    def _create_context_text(
        self,
        messages: List[Dict[str, str]],
        candidate_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create searchable text from conversation context
        
        Args:
            messages: Conversation messages
            candidate_data: Candidate information
            
        Returns:
            Formatted context text
        """
        # Format messages
        message_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages[-10:]  # Last 10 messages
        ])
        
        # Format candidate data
        candidate_text = ""
        if candidate_data:
            candidate_text = f"\n\nCandidate Info:\n{json.dumps(candidate_data, indent=2)}"
        
        return f"Conversation:\n{message_text}{candidate_text}"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector DB collection
        
        Returns:
            Collection statistics
        """
        count = self.collection.count()
        return {
            "total_contexts": count,
            "collection_name": settings.CHROMA_COLLECTION_NAME
        }


# Global vector DB service instance
vector_db_service = VectorDBService()
