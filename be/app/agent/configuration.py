"""Define the configurable parameters for the agent."""

from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Optional, Literal
from langchain_core.runnables import RunnableConfig, ensure_config
from ..core.config import Config


@dataclass
class Configuration:
    """The configuration for the agent."""

    system_prompt: str = field(
        default="""Bạn là DVC.AI, một trợ lý ảo thông minh chuyên về dịch vụ công và thủ tục hành chính Việt Nam.

Tính cách và phong cách:
- Thân thiện, chuyên nghiệp và luôn sẵn sàng hỗ trợ
- Sử dụng tiếng Việt tự nhiên, dễ hiểu
- Kiên nhẫn và chi tiết trong giải thích
- Luôn cập nhật thông tin chính xác

Khả năng:
- Tìm kiếm thông tin từ cơ sở dữ liệu thủ tục hành chính
- Hướng dẫn chi tiết các quy trình, thủ tục
- Tư vấn về giấy tờ cần thiết và cách thức thực hiện
- Ghi nhớ ngữ cảnh cuộc trò chuyện để hỗ trợ tốt hơn

Quy tắc:
1. Luôn sử dụng thông tin từ cơ sở dữ liệu để trả lời
2. Nếu không tìm thấy thông tin, hãy thành thật nói rằng cần tìm hiểu thêm
3. Cung cấp thông tin từng bước rõ ràng
4. Hỏi lại nếu câu hỏi chưa rõ ràng
5. Đề xuất các câu hỏi liên quan để hỗ trợ tốt hơn

Thời gian hiện tại: {system_time}
Thông tin bổ sung:
{memories}""",
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
                          "This prompt sets the context and behavior for the agent."
        },
    )

    temperature: float = field(
        default=Config.OPENAI_TEMPERATURE,
        metadata={
            "description": "The temperature parameter for the agent's interactions. "
                          "A higher temperature leads to more creative and diverse responses, "
                          "while a lower temperature results in more deterministic and coherent responses."
        },
    )
    
    max_tokens: int = field(
        default=2000,
        metadata={"description": "The maximum number of tokens to generate for the agent's responses."}
    )

    timeout: int = field(
        default=120,
        metadata={"description": "The maximum time in seconds to wait for the agent's responses."}
    )

    model: str = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
                          "Should be in the form: provider/model-name."
        },
    )

    retriever_provider: Literal["milvus", "chroma", "elastic"] = field(default="milvus")
    
    embed_model: str = field(
        default="openai/text-embedding-3-small",
        metadata={
            "description": "The name of the embedding model to use for generating embeddings for text. "
                          "Should be in the form: provider:model-name."
        },
    )

    max_search_results: int = field(
        default=5,
        metadata={
            "description": "The maximum number of search results to return for each search query."
        },
    )

    search_threshold: float = field(
        default=0.7,
        metadata={"description": "The search threshold for each search query."}
    )

    @classmethod
    def from_runnable_config(
            cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
