"""Natural Language Processing for JARVIS."""
import os
from typing import Any, Dict, List, Optional, Tuple
import json

import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import spacy
import faiss

from ..config import Config
from ..utils.exceptions import ConfigError

class NLPManager:
    """Handle natural language processing tasks."""
    
    def __init__(self, config: Config):
        """Initialize NLP manager.
        
        Args:
            config: JARVIS configuration instance
        """
        self.config = config
        
        # Load models
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize FAISS index for semantic search
        self.embedding_dim = 384  # Dimension of sentence embeddings
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.stored_texts = []
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            result = self.sentiment_analyzer(text)[0]
            return {
                'label': result['label'],
                'score': result['score'],
                'is_positive': result['label'] == 'POSITIVE'
            }
        except Exception as e:
            return {'label': 'NEUTRAL', 'score': 0.5, 'is_positive': True}
    
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of dictionaries containing entity information
        """
        doc = self.nlp(text)
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
    
    def get_intent(self, text: str) -> Dict[str, Any]:
        """Determine user intent from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing intent classification
        """
        # Extract key verbs and objects
        doc = self.nlp(text)
        verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
        objects = [token.text for token in doc if token.dep_ in ('dobj', 'pobj')]
        
        # Basic intent classification
        intent = {
            'action': verbs[0] if verbs else None,
            'target': objects[0] if objects else None,
            'confidence': 0.0
        }
        
        # TODO: Implement more sophisticated intent classification
        # For now, use basic rule-based approach
        if any(word in text.lower() for word in ['search', 'find', 'look']):
            intent.update({'category': 'search', 'confidence': 0.8})
        elif any(word in text.lower() for word in ['open', 'launch', 'start']):
            intent.update({'category': 'launch', 'confidence': 0.8})
        elif any(word in text.lower() for word in ['close', 'exit', 'stop']):
            intent.update({'category': 'stop', 'confidence': 0.8})
        else:
            intent.update({'category': 'unknown', 'confidence': 0.5})
            
        return intent
    
    def add_to_knowledge(self, text: str, metadata: Optional[Dict] = None) -> int:
        """Add text to semantic search index.
        
        Args:
            text: Text to add
            metadata: Optional metadata about the text
            
        Returns:
            Index of added text
        """
        embedding = self.embedder.encode([text])[0]
        self.index.add(np.array([embedding]))
        self.stored_texts.append({
            'text': text,
            'metadata': metadata or {}
        })
        return len(self.stored_texts) - 1
    
    def semantic_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for semantically similar texts.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        query_embedding = self.embedder.encode([query])[0]
        distances, indices = self.index.search(
            np.array([query_embedding]), k
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.stored_texts):
                result = self.stored_texts[idx].copy()
                result['similarity'] = 1 - (dist / 2)  # Convert distance to similarity
                results.append(result)
                
        return results
    
    def extract_keywords(self, text: str) -> List[Dict[str, Any]]:
        """Extract important keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of dictionaries containing keyword information
        """
        doc = self.nlp(text)
        keywords = []
        
        for token in doc:
            if token.is_stop or token.is_punct:
                continue
            if token.pos_ in ('NOUN', 'PROPN', 'ADJ', 'VERB'):
                keywords.append({
                    'text': token.text,
                    'lemma': token.lemma_,
                    'pos': token.pos_,
                    'importance': token.prob  # Log probability (lower is more important)
                })
                
        # Sort by importance
        keywords.sort(key=lambda x: x['importance'])
        return keywords[:10]  # Return top 10 keywords 