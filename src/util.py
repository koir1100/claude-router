
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
        
        # Only convert supported tools
        if name in SUPPORTED_CLAUDE_TOOLS:
            # Use proper Ollama format with type: "function" wrapper
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

# -----------------------------
# 3. 메시지 변환 함수
# -----------------------------
def convert_messages_to_ollama_format(messages):
    """Convert Anthropic messages or string to Ollama chat format"""
    ollama_messages = []
    print(f"Convert messages: {messages}")
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if isinstance(content, list):
            # Handle Claude Code tool_result messages
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
            
            # Combine text and tool results
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
    """Generate perfect instruction for all Claude Code scenarios"""
    
    base_instruction = f"""You are Claude Code assistant. Tools available: {', '.join([tool['function']['name'] for tool in ollama_tools])}

CRITICAL DECISION TREE:
1. Is this a COMPLEX/MULTI-STEP request? (creating multiple files, implementing features, building services, etc.)
   → YES: IMMEDIATELY use TodoWrite to plan all steps, then execute each step
   → NO: Continue to step 2

2. Is this a SINGLE ACTION? (read one file, run one command, edit one thing)
   → YES: Use the appropriate tool directly
   → NO: Continue to step 3

3. Is this a QUESTION/EXPLANATION? (asking about concepts, seeking information)
   → YES: Answer with text

MULTI-STEP INDICATORS (ALWAYS use TodoWrite first):
- "개발/develop/create/build/implement/make"
- "구성/structure/organize"  
- "모든/all files"
- Multiple requirements in one request
- Mentions folders + files + code

TodoWrite FORMAT:
{{"todos": [{{"content": "Clear task description", "status": "pending", "activeForm": "Doing the task"}}]}}

EXAMPLES:
- "auth 서비스 개발" → TodoWrite immediately
- "README 읽어줘" → Read tool directly  
- "FastAPI가 뭐야?" → Text answer

NEVER give explanations about tool errors - just use tools correctly."""
    
    return base_instruction

def add_tool_instruction(payload, ollama_tools, messages):
    payload["tools"] = ollama_tools
    print(f"🛠️  Added {len(ollama_tools)} tools to Ollama request:")
    for tool in ollama_tools:
        print(f"   - {tool['function']['name']}")
    
    # 강화된 상세 지침 생성
    system_instruction = build_detailed_tool_instruction(ollama_tools)
    
    # Add system message at the beginning instead of embedding in user message
    system_message = {
        "role": "system", 
        "content": system_instruction
    }
    
    # Insert system message at the beginning
    messages.insert(0, system_message)
    
    print(f"🚨 Added system instruction with {len(system_instruction)} characters")
    print(f"🚨 First 200 chars: {system_instruction[:200]}...")
    
    # Debug: Print the full system instruction to see what we're sending
    print(f"🔍 FULL SYSTEM INSTRUCTION BEING SENT:")
    print("-" * 80)
    print(system_instruction)
    print("-" * 80)

# 비밀키 (서비스 시작 시 고정된 random key 사용 권장)
from src.const import DEFAULT_SIGNATURE_SECRET
SECRET_KEY = os.getenv("SIGNATURE_SECRET", DEFAULT_SIGNATURE_SECRET)

def generate_signature(text: str) -> str:
    """
    thinking 텍스트 블록에 대해 무결성 서명을 생성
    HMAC-SHA256 + base64 인코딩
    """
    if not text:
        return ""

    sig = hmac.new(
        SECRET_KEY.encode("utf-8"),
        text.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(sig).decode("utf-8")