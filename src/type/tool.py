from dataclasses import dataclass, field
from typing import Any, Dict, List

# Ollama Tool Types
@dataclass
class OllamaToolFunction:
    name: str
    description: str
    parameters: object

@dataclass
class OllamaTool:
    function: OllamaToolFunction
    type: str = "function"

# Claude Tool Types
@dataclass
class ClaudeToolInputSchema:
    type: str = "object"
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    additionalProperties: bool = False

@dataclass
class ClaudeTool:
    name: str
    description: str
    input_schema: ClaudeToolInputSchema = field(default_factory=ClaudeToolInputSchema)

@dataclass
class ClaudeToolCall:
    type: str = "tool_use"
    id: str = ""
    name: str = ""
    input: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ClaudeToolResult:
    type: str = "tool_result"
    tool_use_id: str = ""
    content: str = ""
    is_error: bool = False

# Tool Function Call (for Ollama responses)
@dataclass
class ToolFunctionCall:
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolCall:
    function: ToolFunctionCall
    type: str = "function"