from dataclasses import dataclass, field
import dataclasses
from enum import Enum
from typing import Optional
import uuid

from src.deco import print_dataclass_values


class Event(Enum):
    message_start = "message_start"
    content_block_start = "content_block_start"
    content_block_delta = "content_block_delta"
    content_block_stop = "content_block_stop"
    message_delta = "message_delta"
    message_stop = "message_stop"
    error = "error"

@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

@dataclass
class MessageUsage:
    output_tokens: int = 0

@dataclass
class Message:
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    type: str = "message"
    role: str = "assistant"
    model: str = ""
    content: list[any] = field(default_factory=list)
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Usage = field(default_factory=Usage)

@dataclass
class MessageStart:
    type: str = Event.message_start.value
    message: Message = None

@dataclass
class ContentBlock:
    type: str = "text"
    text: str = ""

@dataclass
class ContentBlockDeltaDelta:
    type: str = "text_delta"
    text: str = ""

@dataclass
class ContentBlockThinking:
    type: str = "thinking"
    thinking: str = ""

@dataclass
class ContentBlockThinkingDeltaDelta:
    type: str = "thinking_delta"
    thinking: str = ""

@dataclass
class ContentBlockSignatureDeltaDelta:
    type: str = "signature_delta"
    signature: str = ""

@dataclass
class ContentBlockToolStartDelta:
    name: str
    input: object
    type: str = "tool_use"
    id: str = field(default_factory=lambda: f"toolu_{uuid.uuid4().hex[:12]}")
    
@dataclass
class ContentBlockToolDeltaDelta:
    type: str = "input_json_delta"
    partial_json: str = ""

@dataclass
class ContentBlockToolUseDelta:
    type: str = "input_json_delta"
    partial_json: str = ""

@dataclass
class ContentBlockToolUse:
    type: str = "tool_use"
    id: str = ""
    name: str = ""

@dataclass
class ContentBlockStart:
    type: str = Event.content_block_start.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지
    content_block: any = field(default_factory=ContentBlock)

@dataclass
class ContentBlockDelta:
    type: str = Event.content_block_delta.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지
    delta: ContentBlockDeltaDelta = field(default_factory=ContentBlockDeltaDelta)

@dataclass
class ContentBlockThinkingStart:
    type: str = Event.content_block_start.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지
    content_block: ContentBlockThinking = field(default_factory=ContentBlockThinking)

@dataclass
class ContentBlockThinkingDelta:
    type: str = Event.content_block_delta.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지
    delta: ContentBlockThinkingDeltaDelta = field(default_factory=ContentBlockThinkingDeltaDelta)

@dataclass
class ContentBlockSignatureDelta:
    type: str = Event.content_block_delta.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지
    delta: ContentBlockSignatureDeltaDelta = field(default_factory=ContentBlockSignatureDeltaDelta)

@dataclass
class ContentBlockToolStart:
    content_block: ContentBlockToolStartDelta
    type: str = Event.content_block_start.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지

@dataclass
class ContentBlockToolDelta:
    type: str = Event.content_block_start.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지
    delta: ContentBlockToolDeltaDelta = field(default_factory=ContentBlockToolDeltaDelta)

@dataclass
class ContentBlockStop:
    type: str = Event.content_block_stop.value
    index: int = -1 # 타입을 int로 변경하여 일관성 유지

@dataclass
class MessageDeltaDelta:
    stop_reason: str = "end_turn"
    stop_sequence: None = None

@dataclass
class MessageDelta:
    type: str = Event.message_delta.value
    delta: MessageDeltaDelta = field(default_factory=MessageDeltaDelta)
    usage: Usage = field(default_factory=Usage)

@dataclass
class MessageStop:
    type: str = Event.message_stop.value

@dataclass
class ErrorMessage:
    type: str = "api_error"
    message: str = "error_message"

@dataclass
class Error:
    type: str = "error"
    error: ErrorMessage = field(default_factory=ErrorMessage)


current_module_members = globals().copy()

for name, obj in current_module_members.items():
    # 멤버가 데이터클래스인지 확인합니다.
    # 단, 자기 자신(데코레이터 함수 등)은 제외합니다.
    if dataclasses.is_dataclass(obj) and obj is not print_dataclass_values:
        # 데코레이터를 직접 호출하여 클래스를 수정하고,
        # 수정된 클래스를 다시 전역 멤버에 할당합니다.
        decorated_class = print_dataclass_values(obj)
        globals()[name] = decorated_class