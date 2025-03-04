"""Conversation management for JARVIS."""
import random
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..config import Config
from ..utils.exceptions import ConversationError

class ConversationManager:
    """Manage conversations and responses."""
    
    def __init__(self, config: Config):
        """Initialize conversation manager.
        
        Args:
            config: JARVIS configuration instance
        """
        self.config = config
        self.context: Dict[str, Any] = {
            'last_interaction': None,
            'current_mood': 'neutral',
            'conversation_history': []
        }
        
    def get_response(self, category: str, subcategory: str = None, 
                    mood: str = None) -> str:
        """Get an appropriate response based on category and mood.
        
        Args:
            category: Response category (e.g., 'greetings', 'acknowledgments')
            subcategory: Optional subcategory
            mood: Optional mood override
            
        Returns:
            Selected response string
            
        Raises:
            ConversationError: If response cannot be retrieved
        """
        try:
            mood = mood or self.context['current_mood']
            responses = self.config.get_response(category)
            
            if not responses:
                raise ConversationError(f"No responses found for category: {category}")
                
            if subcategory:
                responses = responses.get(subcategory, responses)
                
            if isinstance(responses, dict) and mood in responses:
                responses = responses[mood]
                
            if isinstance(responses, list):
                return random.choice(responses)
            return str(responses)
            
        except Exception as e:
            raise ConversationError(f"Failed to get response: {str(e)}")
    
    def update_context(self, **kwargs) -> None:
        """Update conversation context.
        
        Args:
            **kwargs: Key-value pairs to update in context
        """
        self.context.update(kwargs)
        self.context['last_interaction'] = datetime.now()
    
    def add_to_history(self, speaker: str, message: str) -> None:
        """Add a message to conversation history.
        
        Args:
            speaker: Who said the message ('user' or 'jarvis')
            message: The message content
        """
        self.context['conversation_history'].append({
            'timestamp': datetime.now(),
            'speaker': speaker,
            'message': message
        })
        
    def get_wake_phrases(self) -> List[str]:
        """Get list of wake phrases.
        
        Returns:
            List of wake phrases
        """
        return self.config.get_response('wake_phrases', default=[])
    
    def analyze_mood(self, message: str) -> str:
        """Analyze message to determine appropriate mood.
        
        Args:
            message: User's message
            
        Returns:
            Detected mood ('happy', 'sad', 'neutral', 'energetic')
        """
        # TODO: Implement more sophisticated mood detection
        # For now, use simple keyword matching
        if any(word in message.lower() for word in ['great', 'awesome', 'amazing']):
            return 'happy'
        elif any(word in message.lower() for word in ['sad', 'tired', 'upset']):
            return 'sad'
        elif any(word in message.lower() for word in ['lets go', 'come on', 'hurry']):
            return 'energetic'
        return 'neutral' 