"""
OpenAI Service

Direct integration with OpenAI API for embeddings and chat completions.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..core.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        """Initialize OpenAI service"""
        self.api_key = Config.OPENAI_API_KEY
        self.embedding_model = Config.OPENAI_EMBEDDING_MODEL
        self.chat_model = Config.OPENAI_CHAT_MODEL
        self.temperature = Config.OPENAI_TEMPERATURE
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.timeout = Config.OPENAI_TIMEOUT
        
        # Initialize OpenAI client
        self.client = None
        self.enabled = False
        
        self._setup_client()
    
    def _setup_client(self):
        """Setup OpenAI client"""
        try:
            if not self.api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
                return False
            
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=self.timeout
            )
            
            # Test connection
            self._test_connection()
            self.enabled = True
            logger.info("OpenAI client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
            self.enabled = False
            return False
    
    def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            # Test with a simple embedding request
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input="Test connection"
            )
            logger.info("OpenAI API connection test successful")
            return True
        except Exception as e:
            logger.warning(f"OpenAI API connection test failed: {e}")
            raise e
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.enabled:
            logger.error("OpenAI service is not enabled")
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated embeddings for {len(texts)} texts using model: {self.embedding_model}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the API call
            
        Returns:
            Generated response text
        """
        if not self.enabled:
            logger.error("OpenAI service is not enabled")
            return "OpenAI service is not available."
        
        try:
            # Merge default parameters with provided kwargs
            params = {
                "model": self.chat_model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **kwargs
            }
            
            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            logger.info(f"Generated chat completion with {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            return f"Error generating response: {str(e)}"
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the current model
        
        Returns:
            Embedding dimension
        """
        model_dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536
        }
        
        return model_dimensions.get(self.embedding_model, 1536)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "enabled": self.enabled,
            "embedding_model": self.embedding_model,
            "chat_model": self.chat_model,
            "embedding_dimension": self.get_embedding_dimension(),
            "api_key_configured": bool(self.api_key)
        }


# Global OpenAI service instance
openai_service = OpenAIService()
