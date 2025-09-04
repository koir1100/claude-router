from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import uuid

# Anthropic/Claude Streaming Protocol Dataclasses

class Event(Enum):
    message_start = "message_start"
    content_block_start = "content_block_start"
    content_block_delta = "content_block_delta"
    content_block_stop = "content_block_stop"
    message_delta = "message_delta"
    message_stop = "message_stop"
    error = "error"
    ping = "ping"

@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

@dataclass
class Message:
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    type: str = "message"
    role: str = "assistant"
    model: str = ""
    content: list = field(default_factory=list)
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Usage = field(default_factory=Usage)

@dataclass
class MessageStart:
    type: str = Event.message_start.value
    message: Message = field(default_factory=Message)

@dataclass
class ContentBlock:
    type: str = "text"
    text: str = ""

@dataclass
class ContentBlockStart:
    type: str = Event.content_block_start.value
    index: int = 0
    content_block: ContentBlock = field(default_factory=ContentBlock)

@dataclass
class ContentBlockDeltaDelta:
    type: str = "text_delta"
    text: str = ""

@dataclass
class ContentBlockDelta:
    type: str = Event.content_block_delta.value
    index: int = 0
    delta: ContentBlockDeltaDelta = field(default_factory=ContentBlockDeltaDelta)

@dataclass
class ContentBlockStop:
    type: str = Event.content_block_stop.value
    index: int = 0

@dataclass
class MessageDeltaDelta:
    stop_reason: str = "end_turn"
    stop_sequence: Optional[str] = None

@dataclass
class MessageDeltaUsage:
    output_tokens: int = 0

@dataclass
class MessageDelta:
    type: str = Event.message_delta.value
    delta: MessageDeltaDelta = field(default_factory=MessageDeltaDelta)
    usage: MessageDeltaUsage = field(default_factory=MessageDeltaUsage)

@dataclass
class MessageStop:
    type: str = Event.message_stop.value

@dataclass
class ErrorMessage:
    type: str = "error"
    message: str = ""

@dataclass
class Error:
    type: str = "error"
    error: ErrorMessage = field(default_factory=ErrorMessage)

@dataclass
class ContentBlockThinking:
    type: str = "thinking"

@dataclass
class ContentBlockThinkingStart:
    type: str = "content_block_start"
    index: int = 0
    content_block: ContentBlockThinking = field(default_factory=ContentBlockThinking)

@dataclass
class ContentBlockThinkingDeltaDelta:
    type: str = "thinking_delta"
    thinking: str = ""

@dataclass
class ContentBlockThinkingDelta:
    type: str = "content_block_delta"
    index: int = 0
    delta: ContentBlockThinkingDeltaDelta = field(default_factory=ContentBlockThinkingDeltaDelta)

@dataclass
class ContentBlockSignatureDeltaDelta:
    type: str = "signature_delta"
    signature: str = ""

@dataclass
class ContentBlockSignatureDelta:
    type: str = "content_block_delta"
    index: int = 0
    delta: ContentBlockSignatureDeltaDelta = field(default_factory=ContentBlockSignatureDeltaDelta)

@dataclass
class ContentBlockToolUse:
    type: str = "tool_use"
    id: str = ""
    name: str = ""
    input: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentBlockToolUseDelta:
    type: str = "input_json_delta"
    partial_json: str = ""