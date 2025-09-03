"""Define the state structures for the agent."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence, List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated


@dataclass
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    session_id: str = field(default="")
    user_id: str = field(default="anonymous")
    memories: dict = field(default_factory=dict)
    """
    Messages tracking the primary execution state of the agent.

    Typically accumulates a pattern of:
    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    4. AIMessage without .tool_calls - agent responding in unstructured format to the user
    5. HumanMessage - user responds with the next conversational turn

    Steps 2-5 may repeat as needed.

    The `add_messages` annotation ensures that new messages are merged with existing ones,
    updating by ID to maintain an "append-only" state unless a message with the same ID is provided.
    """


@dataclass
class State(InputState):
    """Represents the complete state of the agent, extending InputState with additional attributes.

    This class can be used to store any information needed throughout the agent's lifecycle.
    """

    is_last_step: IsLastStep = field(default=False)
    context: Dict[str, Any] = field(default_factory=dict)
    needs_search: bool = field(default=False)
    route_destination: str = field(default="casual")
    language: str = field(default="vi")
    """
    Indicates whether the current step is the last one before the graph raises an error.

    This is a 'managed' variable, controlled by the state machine rather than user code.
    It is set to 'True' when the step count reaches recursion_limit - 1.
    """


@dataclass
class ChatState(InputState):
    """The state of the chatbot with RAG capabilities."""

    is_last_step: IsLastStep = field(default=False)
    better_query: Optional[str] = field(default="")
    generation: Optional[str] = field(default="")
    documents: List[Document] = field(default_factory=list)
    use_filter: bool = field(default=False)
    retrieved_documents: List[str] = field(default_factory=list)
    language: str = field(default='vi')
    extracted_entities: List[str] = field(default_factory=list)
    source_info: str = field(default="")
    confidence: float = field(default=0.0)
    needs_search: bool = field(default=False)
    route_destination: str = field(default="other")
