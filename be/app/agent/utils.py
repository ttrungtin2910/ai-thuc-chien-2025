"""Utility functions for the agent system."""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.documents import Document


def get_current_datetime() -> str:
    """Get current datetime in Vietnamese timezone."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def detect_language(text: str) -> str:
    """Simple language detection for Vietnamese/English."""
    vietnamese_chars = re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower())
    if vietnamese_chars or any(word in text.lower() for word in ['thủ tục', 'hồ sơ', 'giấy tờ', 'đăng ký']):
        return 'vi'
    return 'en'


def format_conversation_history(messages: List[BaseMessage]) -> str:
    """Format conversation history for prompts."""
    if not messages:
        return "Không có lịch sử cuộc trò chuyện."
    
    formatted = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(f"Người dùng: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted.append(f"Trợ lý: {msg.content}")
        elif isinstance(msg, SystemMessage):
            continue  # Skip system messages in history
    
    return "\n".join(formatted[-6:])  # Last 6 messages


def get_ai_and_human_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """Filter out system messages and return only AI and Human messages."""
    return [msg for msg in messages if isinstance(msg, (HumanMessage, AIMessage))]


def group_by_format_documents(documents: List[Document]) -> tuple[str, Dict[str, Any]]:
    """Format documents for context and return document mapping."""
    if not documents:
        return "Không có tài liệu liên quan.", {}
    
    context_parts = []
    doc_mapping = {}
    
    for i, doc in enumerate(documents, 1):
        title = doc.metadata.get('title', 'Tài liệu không tên')
        section = doc.metadata.get('section', 'Phần không xác định')
        content = doc.page_content
        
        context_part = f"[{i}] {title} - {section}\n{content}"
        context_parts.append(context_part)
        
        doc_mapping[str(i)] = {
            'document': doc,
            'title': title,
            'section': section,
            'content': content
        }
    
    return "\n\n".join(context_parts), doc_mapping


def get_doc_source_id(citations: List[str], docs: Dict[str, Any]) -> List[Document]:
    """Extract cited documents based on citation numbers."""
    cited_docs = []
    
    for citation in citations:
        if citation in docs:
            cited_docs.append(docs[citation]['document'])
    
    return cited_docs


def format_source_info(documents: List[Document], language: str = 'vi') -> str:
    """Format source information for display."""
    if not documents:
        return ""
    
    if language == 'vi':
        source_header = "Nguồn tham khảo:"
    else:
        source_header = "Sources:"
    
    sources = []
    for i, doc in enumerate(documents, 1):
        title = doc.metadata.get('title', 'Unknown Document')
        section = doc.metadata.get('section', 'Unknown Section')
        sources.append(f"{i}. {title} - {section}")
    
    return f"\n\n{source_header}\n" + "\n".join(sources)


def dict_to_xml(data: Dict[str, Any]) -> str:
    """Convert dictionary to simple XML format for prompts."""
    if not data:
        return "<memories>Không có thông tin bổ sung</memories>"
    
    xml_parts = ["<memories>"]
    for key, value in data.items():
        xml_parts.append(f"<{key}>{value}</{key}>")
    xml_parts.append("</memories>")
    
    return "\n".join(xml_parts)


def clean_query(query: str) -> str:
    """Clean and normalize user query."""
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Remove common noise words
    noise_words = ['ơi', 'này', 'kia', 'ạ', 'ah', 'uhm']
    for word in noise_words:
        query = re.sub(f'\\b{word}\\b', '', query, flags=re.IGNORECASE)
    
    return query.strip()


def calculate_confidence(documents: List[Document]) -> float:
    """Calculate confidence score based on document relevance."""
    if not documents:
        return 0.0
    
    # Use the highest score from documents
    scores = []
    for doc in documents:
        score = doc.metadata.get('score', 0.0)
        if isinstance(score, (int, float)):
            scores.append(float(score))
    
    if not scores:
        return 0.5  # Default confidence
    
    return max(scores)


def should_use_rag(query: str) -> bool:
    """Determine if query requires RAG search."""
    query_lower = query.lower()
    
    # Keywords that require RAG
    rag_keywords = [
        'thủ tục', 'hồ sơ', 'giấy tờ', 'đăng ký', 'cấp', 'làm',
        'xin', 'nộp', 'phí', 'lệ phí', 'thời gian', 'quy trình',
        'bao lâu', 'ở đâu', 'như thế nào', 'cần gì', 'yêu cầu',
        'điều kiện', 'địa chỉ', 'cơ quan', 'văn phòng'
    ]
    
    # Question indicators
    question_words = ['?', 'như thế nào', 'ra sao', 'thế nào', 'tại sao', 'vì sao']
    
    has_rag_keyword = any(keyword in query_lower for keyword in rag_keywords)
    has_question = any(word in query_lower for word in question_words)
    
    return has_rag_keyword or has_question
