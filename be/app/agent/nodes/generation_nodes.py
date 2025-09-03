"""Response generation nodes."""

import logging
from langchain_core.messages import trim_messages, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from .base_node import BaseNode
from ..state import ChatState
from ..configuration import Configuration
from ..chains import get_generation_chain, load_chat_model
from ..utils import (
    get_ai_and_human_messages, 
    group_by_format_documents, 
    get_doc_source_id, 
    format_source_info,
    get_current_datetime,
    dict_to_xml
)

logger = logging.getLogger(__name__)


class ContextGeneratorNode(BaseNode):
    """Node to generate response using retrieved context."""
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Generate response with citations using retrieved documents."""
        try:
            # Prepare conversation messages
            messages = trim_messages(
                messages=state.messages,
                strategy="last",
                token_counter=len,
                max_tokens=5,
                start_on="human",
                end_on="human",
                allow_partial=False,
            )
            
            valid_messages = get_ai_and_human_messages(messages)
            question = valid_messages[-1].content if valid_messages else ""
            
            # Format documents as context
            context, docs_mapping = group_by_format_documents(state.documents)
            
            # Language mapping
            language_mapping = {
                'vi': 'tiếng Việt',
                'en': 'English'
            }
            language = language_mapping.get(state.language, 'tiếng Việt')
            
            # Generate response with citations
            generation_chain = get_generation_chain()
            inputs = {
                "messages": valid_messages,
                "context": context,
                "question": question,
                "language": language
            }
            
            cited_response = await generation_chain.ainvoke(inputs, config=config)
            
            logger.info(f"Generated response with {len(cited_response.citations)} citations")
            
            # Get cited documents
            cited_docs = get_doc_source_id(cited_response.citations, docs_mapping)
            
            return {
                "generation": cited_response.answer,
                "documents": cited_docs,
                "extracted_entities": cited_response.citations  # Store citation numbers
            }
            
        except Exception as e:
            logger.error(f"Error in context generation: {e}")
            return {
                "generation": "Xin lỗi, có lỗi xảy ra khi tạo phản hồi.",
                "documents": [],
                "extracted_entities": []
            }


class GenericResponseNode(BaseNode):
    """Node to generate generic conversational responses."""
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Generate casual conversational response."""
        try:
            configuration = Configuration.from_runnable_config(config)
            
            # Get conversation history
            messages = trim_messages(
                messages=state.messages,
                strategy="last",
                token_counter=len,
                max_tokens=4,
                start_on="human",
                end_on="human",
                allow_partial=True,
            )
            
            valid_messages = get_ai_and_human_messages(messages)
            
            # Create system message
            system_message = configuration.system_prompt.format(
                system_time=get_current_datetime(),
                memories=dict_to_xml(state.memories)
            )
            
            # Load model and generate response
            model = load_chat_model(configuration.model)
            
            response = await model.ainvoke([
                SystemMessage(content=system_message),
                *valid_messages
            ], config=config)
            
            logger.info("Generated generic response")
            
            return {
                "generation": response.content,
                "documents": [],
                "extracted_entities": []
            }
            
        except Exception as e:
            logger.error(f"Error in generic response generation: {e}")
            return {
                "generation": "Xin lỗi, có lỗi xảy ra khi tạo phản hồi.",
                "documents": [],
                "extracted_entities": []
            }


class PostProcessNode(BaseNode):
    """Node to post-process and format final response."""
    
    async def __call__(self, state: ChatState, config: RunnableConfig) -> dict:
        """Post-process the generated response."""
        try:
            generation = state.generation
            language = state.language
            
            # Default messages
            if language == 'vi':
                no_context_msg = "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn."
            else:
                no_context_msg = "Sorry, I couldn't find relevant information for your question."
            
            # Check if we have a valid response
            if not generation or 'no_answer' in generation.lower():
                final_response = no_context_msg
                source_info = ""
            elif state.documents:
                # Add source information if we have documents
                final_response = generation
                source_info = format_source_info(state.documents, language)
            else:
                final_response = generation
                source_info = ""
            
            logger.info("Post-processed response")
            
            return {
                "generation": final_response,
                "source_info": source_info
            }
            
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
            return {
                "generation": "Xin lỗi, có lỗi xảy ra trong quá trình xử lý.",
                "source_info": ""
            }
