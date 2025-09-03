"""Query transformation nodes."""

import logging
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnableConfig

from .base_node import BaseNode
from ..state import ChatState
from ..chains import get_query_transform_chain
from ..utils import format_conversation_history, clean_query

logger = logging.getLogger(__name__)


class TransformQueryNode(BaseNode):
    """Node to transform and optimize user query for search."""
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Transform user query based on conversation context."""
        try:
            if not state.messages:
                return {"better_query": ""}
            
            # Get conversation history
            messages = trim_messages(
                messages=state.messages,
                strategy="last",
                token_counter=len,
                max_tokens=8,
                start_on="human",
                end_on="human",
                allow_partial=True,
            )
            
            # Format conversation history
            chat_history = format_conversation_history(messages)
            current_question = messages[-1].content if messages else ""
            
            # Clean the query
            cleaned_question = clean_query(current_question)
            
            # Get language mapping
            language_mapping = {
                'vi': 'tiếng Việt',
                'en': 'English'
            }
            language = language_mapping.get(state.language, 'tiếng Việt')
            
            # Transform query
            transform_chain = get_query_transform_chain()
            transform_result = await transform_chain.ainvoke({
                "chat_history": chat_history,
                "question": cleaned_question,
                "language": language
            })
            
            better_query = transform_result.content.strip()
            
            logger.info(f"Query transformed: '{current_question}' -> '{better_query}'")
            
            return {
                "better_query": better_query,
                "use_filter": False  # Could be enhanced based on conversation context
            }
            
        except Exception as e:
            logger.error(f"Error in query transformation: {e}")
            # Fallback to original query
            original_query = state.messages[-1].content if state.messages else ""
            return {
                "better_query": clean_query(original_query),
                "use_filter": False
            }
