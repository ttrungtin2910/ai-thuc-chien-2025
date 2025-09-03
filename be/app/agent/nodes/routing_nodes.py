"""Routing and analysis nodes for query processing."""

import logging
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnableConfig

from .base_node import BaseNode
from ..state import ChatState
from ..chains import get_route_chain
from ..utils import get_ai_and_human_messages, detect_language

logger = logging.getLogger(__name__)


class AnalyzeQueryNode(BaseNode):
    """Node to analyze incoming query and determine processing route."""
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Analyze user query to determine route and language."""
        try:
            # Get the latest user message
            if not state.messages:
                logger.warning("No messages in state")
                return {
                    "needs_search": False,
                    "route_destination": "casual",
                    "language": "vi"
                }
            
            last_message = state.messages[-1]
            query = last_message.content
            
            # Detect language
            language = detect_language(query)
            
            # Prepare messages for routing
            messages = trim_messages(
                messages=state.messages,
                strategy="last",
                token_counter=len,
                max_tokens=8,
                start_on="human",
                end_on="human",
                allow_partial=True,
            )
            
            valid_messages = get_ai_and_human_messages(messages)
            
            # Get routing decision
            route_chain = get_route_chain(config)
            route_result = await route_chain.ainvoke({
                "messages": valid_messages[:-1] if len(valid_messages) > 1 else [],
                "user": query
            })
            
            needs_search = route_result.destination == "other"
            
            logger.info(f"Query analysis: route={route_result.destination}, language={language}, needs_search={needs_search}")
            
            return {
                "route_destination": route_result.destination,
                "needs_search": needs_search,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return {
                "needs_search": False,
                "route_destination": "casual",
                "language": "vi"
            }
