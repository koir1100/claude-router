import base64
from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import os
import uuid

from src.type import Message, MessageStart


@dataclass
class OllamaToolFunction:
    name: str
    description: str
    parameters: object

@dataclass
class OllamaTool:
    function: OllamaToolFunction
    type: str = "function"

def convert_claude_tools_to_ollama(claude_tools):
    """Convert Claude Code tools to Ollama format"""
    from src.const import SUPPORTED_CLAUDE_TOOLS
    ollama_tools = []
    
    for tool in claude_tools:
        name = tool.get('name', 'unknown')
        description = tool.get('description', '')
        parameters = tool.get('input_schema', {})
        
        if name in SUPPORTED_CLAUDE_TOOLS:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            })
        else:
            print(f"⚠️  Unsupported tool skipped: {name}")
    
    return ollama_tools

def build_message_start(model: str) -> MessageStart:
    return MessageStart(
        message=Message(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            model=model
        )
    )

def convert_messages_to_ollama_format(messages):
    """Convert Anthropic messages or string to Ollama chat format"""
    ollama_messages = []
    print(f"Convert messages: {messages}")
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if isinstance(content, list):
            text_parts = []
            tool_results = []
            
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "tool_result":
                        tool_id = item.get("tool_use_id", "")
                        result_content = item.get("content", "")
                        if item.get("is_error"):
                            tool_results.append(f"Tool {tool_id} error: {result_content}")
                        else:
                            tool_results.append(f"Tool {tool_id} result: {result_content}")
            
            combined_content = " ".join(text_parts)
            if tool_results:
                combined_content += "\n\nTool Results:\n" + "\n".join(tool_results)
            content = combined_content
            
        ollama_messages.append({"role": role, "content": content})
    
    print(f"Converted messages: {ollama_messages}")
    return ollama_messages

def to_sse(event: str, data: object) -> str:
    """dataclass → JSON → SSE 문자열 변환"""
    return f"event: {event}\n" + f"data: {json.dumps(asdict(data), ensure_ascii=False)}\n\n"

def build_detailed_tool_instruction(ollama_tools):
    """Generate strict instruction for Claude Code with Ollama, including tool schema awareness and error handling"""
    
    base_instruction = f"""You are **Claude Code Assistant**.
Available tools: {', '.join([tool['function']['name'] for tool in ollama_tools])}

-------------------------
CRITICAL DECISION TREE
-------------------------
1. COMPLEX or MULTI-STEP request? (e.g., create/build/implement, multiple files, services, or combined requirements)
   → MUST first call **TodoWrite** to plan all steps, then execute sequentially.

2. SINGLE ACTION request? (e.g., read one file, run one command, edit one thing)
   → MUST directly call the correct tool.

3. QUESTION or EXPLANATION request? (e.g., ask about concepts, definitions, background)
   → MUST answer in plain text.

-------------------------
MULTI-STEP TRIGGERS:
- Keywords: "개발", "구현", "create", "build", "implement", "make"
- Mentions of structure/organization of code or folders
- Requests involving multiple files, all files, or combined tasks

-------------------------
MANDATORY TodoWrite FORMAT (JSON only):
{{
  "todos": [
    {{"content": "Clear task description", "status": "pending", "activeForm": "Doing the task"}}
  ]
}}

-------------------------
TOOL USAGE GUIDELINES:
- ALWAYS check the tool's schema before calling.
- Ensure parameter names, types, and required fields match exactly.
- For Bash tool:
  - param `command`: string, required
  - param `runInBackground`: boolean, optional
- Always validate inputs before calling a tool.

-------------------------
TOOL ERROR HANDLING:
- If a tool fails:
  1) Determine the cause from the error message.
  2) Explain concisely to the user what went wrong.
  3) Suggest or provide corrected parameters if possible.
- Never output raw stack traces.
- Do not ignore tool failures; always provide actionable info.

-------------------------
EXAMPLES:
- "auth 서비스 개발" → MUST call TodoWrite immediately.
- "README 읽어줘" → MUST call Read tool directly.
- "FastAPI가 뭐야?" → MUST answer in plain text.

-------------------------
RULES:
- ALWAYS follow the decision tree strictly.
- NEVER output malformed JSON for TodoWrite.
- NEVER output unnecessary explanations about tool internals unless required for user action.
"""
    return base_instruction

def add_tool_instruction(payload, ollama_tools, messages):
    payload["tools"] = ollama_tools
    print(f"🛠️  Added {len(ollama_tools)} tools to Ollama request:")
    for tool in ollama_tools:
        print(f"   - {tool['function']['name']}")
    
    system_instruction = build_detailed_tool_instruction(ollama_tools)
    system_message = {"role": "system", "content": system_instruction}
    messages.insert(0, system_message)
    
    print(f"🚨 Added system instruction with {len(system_instruction)} characters")
    print(f"🚨 First 200 chars: {system_instruction[:200]}...")
    print("🔍 FULL SYSTEM INSTRUCTION BEING SENT:")
    print("-" * 80)
    print(system_instruction)
    print("-" * 80)

from src.const import DEFAULT_SIGNATURE_SECRET
SECRET_KEY = os.getenv("SIGNATURE_SECRET", DEFAULT_SIGNATURE_SECRET)

def generate_signature(text: str) -> str:
    """
    Generate HMAC-SHA256 + Base64 signature for thinking text block integrity
    """
    if not text:
        return ""

    sig = hmac.new(
        SECRET_KEY.encode("utf-8"),
        text.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(sig).decode("utf-8")
