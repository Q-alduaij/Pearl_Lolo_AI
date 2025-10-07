from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import datetime as dt


class Capability(str, Enum):
    CHAT = "chat"
    SOLVE = "solve"
    RAG = "rag"
    TTS = "tts"
    STT = "stt"
    SEARCH = "search"


class Message(BaseModel):
    role: str
    content: str


class Attachment(BaseModel):
    kind: str
    path_or_uri: str
    meta: Dict[str, Any] = {}


class Task(BaseModel):
    intent: Capability
    messages: List[Message]
    params: Dict[str, Any] = {}
    attachments: List[Attachment] = []
    locale: str = "en-GB"
    tz: str = "Asia/Kuwait"
    user_tags: List[str] = []


class Citation(BaseModel):
    source: str
    snippet: Optional[str] = None
    score: Optional[float] = None


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0


class ProviderResult(BaseModel):
    ok: bool
    text: str = ""
    data: Dict[str, Any] = {}
    citations: List[Citation] = []
    usage: Usage = Usage()
    warnings: List[str] = []
    finish_reason: str = "stop"


class Health(BaseModel):
    name: str
    ok: bool
    details: Dict[str, Any] = {}
    checked_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class Provider(ABC):
    name: str
    capabilities: List[Capability]

    @abstractmethod
    def health(self) -> Health: ...

    @abstractmethod
    def invoke(self, task: Task) -> ProviderResult: ...
