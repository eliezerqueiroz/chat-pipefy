"""
Pydantic schemas for chat-related requests and responses.
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class Source(BaseModel):
    content: str
    source: str
    chunk_index: int


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    question: str = Field(..., min_length=1, description="User's question")


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    session_id: str


class HealthResponse(BaseModel):
    status: str
    redis: str
