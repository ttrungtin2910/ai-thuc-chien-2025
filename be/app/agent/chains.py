"""Chain definitions for different agent operations."""

from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .configuration import Configuration
from .prompts import ROUTER_PROMPT, TOXIC_CHECKER_PROMPT, QUERY_TRANSFORM_PROMPT, GENERATION_PROMPT
from ..core.config import Config


class RouteQuery(BaseModel):
    """Route a user query to the most relevant destination."""

    destination: Literal["other", "casual"] = Field(
        default="other",
        description="Given a user question choose to route it to casual or a other request.",
    )


class ToxicityAnalysis(BaseModel):
    """Analysis of the inappropriate content check result."""
    
    toxicity: bool = Field(
        description="Boolean indicating if inappropriate content was detected that should be blocked"
    )
    risk_score: float = Field(
        description="Overall risk score (0.0 - 1.0)"
    )
    details: list = Field(
        description="Additional details about detected risks"
    )


class CitedAnswer(BaseModel):
    """Answer with citations to source documents."""
    
    answer: str = Field(description="The generated answer")
    citations: list[str] = Field(description="List of citation numbers used in the answer")


def load_chat_model(model_name: str) -> ChatOpenAI:
    """Load chat model based on configuration."""
    return ChatOpenAI(
        model=Config.OPENAI_CHAT_MODEL,
        temperature=Config.OPENAI_TEMPERATURE,
        api_key=Config.OPENAI_API_KEY,
        max_tokens=2000
    )


def get_route_chain(config: RunnableConfig):
    """Get routing chain for query classification."""
    configuration = Configuration.from_runnable_config(config)
    model_llm = load_chat_model(configuration.model)
    structured_llm = model_llm.with_structured_output(RouteQuery)

    route_prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_PROMPT),
        MessagesPlaceholder(variable_name="messages", optional=True),
        ("human", "Câu hỏi của người dùng: {user}"),
    ])
    
    return route_prompt | structured_llm


def get_toxicity_chain(config: RunnableConfig):
    """Get toxicity checking chain."""
    configuration = Configuration.from_runnable_config(config)
    model_llm = load_chat_model(configuration.model)
    structured_llm = model_llm.with_structured_output(ToxicityAnalysis)

    toxicity_prompt = ChatPromptTemplate.from_messages([
        ("system", TOXIC_CHECKER_PROMPT),
        ("human", "Nội dung cần kiểm tra: {user}"),
    ])
    
    return toxicity_prompt | structured_llm


def get_query_transform_chain():
    """Get query transformation chain."""
    model_llm = load_chat_model("gpt-4o-mini")
    
    transform_prompt = ChatPromptTemplate.from_template(QUERY_TRANSFORM_PROMPT)
    
    return transform_prompt | model_llm


def get_generation_chain():
    """Get response generation chain with citations."""
    model_llm = load_chat_model("gpt-4o-mini")
    structured_llm = model_llm.with_structured_output(CitedAnswer)
    
    generation_prompt = ChatPromptTemplate.from_template(GENERATION_PROMPT)
    
    return generation_prompt | structured_llm
