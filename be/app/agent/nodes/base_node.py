"""Base node class for all agent nodes."""

from abc import ABC, abstractmethod
from langchain_core.runnables import RunnableConfig
from ..state import ChatState


class BaseNode(ABC):
    """Abstract base class for all nodes in the agent graph."""
    
    @abstractmethod
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Execute the node's logic.
        
        Args:
            state: Current state of the conversation
            config: Runtime configuration
            
        Returns:
            Dictionary with state updates
        """
        pass
