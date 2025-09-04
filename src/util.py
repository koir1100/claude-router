import base64
from dataclasses import asdict, dataclass, MISSING
import hashlib
import hmac
import json
import os
import uuid
from typing import Union
from typing import TYPE_CHECKING

from src.type import Message, MessageStart

if TYPE_CHECKING:
    from src.type.tool import ToolCall, ClaudeToolCall


# Tool types are now imported from src.type.tool

def convert_claude_tools_to_ollama(claude_tools):
    """Convert Claude Code tools to Ollama format"""
    from src.const import SUPPORTED_CLAUDE_TOOLS
    from src.type.tool import OllamaTool, OllamaToolFunction
    
    ollama_tools = []
    
    for tool in claude_tools:
        name = tool.get('name', 'unknown')
        description = tool.get('description', '')
        parameters = tool.get('input_schema', {})
        print(f"Claude Code Tool: {tool}")
        
        if name in SUPPORTED_CLAUDE_TOOLS:
            # Create proper Ollama tool using dataclass
            ollama_function = OllamaToolFunction(
                name=name,
                description=description,
                parameters=parameters
            )
            ollama_tool = OllamaTool(function=ollama_function)
            
            # Convert to dict for API call
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

def map_args_to_tool_class(tool_name: str, args: dict):
    """
    DEPRECATED: Use convert_ollama_tool_call_to_claude() instead.
    
    Maps a dictionary of arguments to the corresponding tool's dataclass instance.
    This version is simplified to be more robust and readable.
    """
    print(f"⚠️  DEPRECATED: map_args_to_tool_class() is deprecated. Use convert_ollama_tool_call_to_claude() instead.")
    from src.type import TOOL_ARG_CLASSES
    from dataclasses import fields

    tool_class = TOOL_ARG_CLASSES.get(tool_name)
    if not tool_class:
        print(f"⚠️  No dataclass mapping found for tool: {tool_name}")
        return args  # Return original args if no class is found

    # Get expected argument names from the dataclass fields
    expected_args = {field.name for field in fields(tool_class)}

    # Filter the received arguments to only include those expected by the dataclass
    filtered_args = {k: v for k, v in args.items() if k in expected_args}

    # Check for and log any unexpected arguments provided by the model
    ignored_keys = set(args.keys()) - expected_args
    if ignored_keys:
        print(f"⚠️  Ignoring unexpected arguments for {tool_name}: {list(ignored_keys)}")

    try:
        # Instantiate the dataclass with the filtered arguments
        instance = tool_class(**filtered_args)
        print(f"✨ Successfully mapped arguments to {tool_name} dataclass.")
        return instance
    except TypeError as e:
        # This will catch errors like missing required arguments
        print(f"❌ TypeError when instantiating {tool_name}: {e}")
        print(f"   Provided args: {filtered_args}")
        return None  # Return None on failure

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


def get_file_content_as_base64(file_path: str) -> str:
    """
    Reads a file and returns its content as a Base64 encoded string.
    """
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def convert_ollama_tool_call_to_claude(ollama_tool_call: 'ToolCall') -> 'ClaudeToolCall':
    """
    Convert Ollama ToolCall dataclass to Claude ClaudeToolCall dataclass with proper argument validation.
    
    Args:
        ollama_tool_call: ToolCall dataclass containing Ollama tool call
        
    Returns:
        ClaudeToolCall: Claude Code compatible tool call format
    """
    from src.type import TOOL_ARG_CLASSES
    from src.type.tool import ClaudeToolCall, ToolCall
    from dataclasses import fields
    
    if not isinstance(ollama_tool_call, ToolCall):
        raise TypeError(f"Expected ToolCall dataclass, got {type(ollama_tool_call)}")
    
    # Extract data from ToolCall dataclass
    tool_name = ollama_tool_call.function.name
    raw_arguments = ollama_tool_call.function.arguments
    
    print(f"🔧 Converting ToolCall: {tool_name}")
    print(f"   Raw arguments: {raw_arguments}")
    
    # Parse arguments if they're in string format
    if isinstance(raw_arguments, str):
        try:
            raw_arguments = json.loads(raw_arguments)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse arguments JSON for {tool_name}: {e}")
            return None
    
    # Get the tool's dataclass for validation
    tool_class = TOOL_ARG_CLASSES.get(tool_name)
    if not tool_class:
        print(f"⚠️  No dataclass mapping found for tool: {tool_name}")
        # Return basic format without validation using dataclass
        return ClaudeToolCall(
            type="tool_use",
            id=f"toolu_{uuid.uuid4().hex[:12]}",
            name=tool_name,
            input=raw_arguments
        )
    
    # Get expected field names and types from dataclass
    expected_fields = {field.name: field.type for field in fields(tool_class)}
    validated_args = {}
    
    # Validate and convert each argument
    for field_name, field_type in expected_fields.items():
        if field_name in raw_arguments:
            value = raw_arguments[field_name]
            
            # Handle special parameter name mappings for Grep tool
            if tool_name == "Grep":
                # Map '-A', '-B', '-C', '-n', '-i' parameters
                if field_name in ['A', 'B', 'C', 'n', 'i']:
                    # These might come as '-A', '-B', etc. from Ollama
                    alt_key = f"-{field_name}"
                    if alt_key in raw_arguments:
                        value = raw_arguments[alt_key]
                    elif field_name not in raw_arguments:
                        continue  # Skip if not present
            
            # Type conversion and validation
            try:
                # Handle optional types
                if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                    # Optional[Type] handling
                    args = field_type.__args__
                    if type(None) in args:
                        # This is Optional[SomeType]
                        non_none_types = [arg for arg in args if arg != type(None)]
                        if non_none_types:
                            target_type = non_none_types[0]
                        else:
                            target_type = str
                    else:
                        target_type = args[0]
                else:
                    target_type = field_type
                
                # Handle List types
                if hasattr(target_type, '__origin__') and target_type.__origin__ is list:
                    if not isinstance(value, list):
                        print(f"⚠️  Expected list for {field_name}, got {type(value)}")
                        continue
                    validated_args[field_name] = value
                # Handle basic types
                elif target_type in [str, int, bool]:
                    if target_type == bool and isinstance(value, str):
                        # Convert string booleans
                        validated_args[field_name] = value.lower() in ['true', '1', 'yes']
                    elif target_type == int and isinstance(value, str):
                        try:
                            validated_args[field_name] = int(value)
                        except ValueError:
                            print(f"⚠️  Could not convert '{value}' to int for {field_name}")
                            continue
                    else:
                        validated_args[field_name] = target_type(value)
                else:
                    # For complex types, just pass through
                    validated_args[field_name] = value
                    
            except (ValueError, TypeError) as e:
                print(f"⚠️  Type conversion error for {field_name}: {e}")
                continue
    
    # Check for required fields
    required_fields = [field.name for field in fields(tool_class) 
                      if field.default == MISSING and field.default_factory == MISSING]
    
    missing_fields = [field for field in required_fields if field not in validated_args]
    if missing_fields:
        print(f"❌ Missing required fields for {tool_name}: {missing_fields}")
        # Still return the tool call, let Claude Code handle the error
    
    # Additional arguments not in dataclass
    extra_args = {k: v for k, v in raw_arguments.items() if k not in expected_fields}
    if extra_args:
        print(f"⚠️  Extra arguments for {tool_name} (will be included): {list(extra_args.keys())}")
        validated_args.update(extra_args)
    
    print(f"✅ Validated arguments for {tool_name}: {validated_args}")
    
    # Return Claude Code format using dataclass
    return ClaudeToolCall(
        type="tool_use",
        id=f"toolu_{uuid.uuid4().hex[:12]}",
        name=tool_name,
        input=validated_args
    )

def dict_to_ollama_tool_call(tool_call_dict: dict) -> 'ToolCall':
    """
    Convert dict format Ollama tool call to ToolCall dataclass.
    
    Args:
        tool_call_dict: Dict containing Ollama tool call with 'function' key
        
    Returns:
        ToolCall: Structured Ollama tool call
    """
    from src.type.tool import ToolCall, ToolFunctionCall
    
    if not isinstance(tool_call_dict, dict) or 'function' not in tool_call_dict:
        raise ValueError(f"Invalid tool call dict format: {tool_call_dict}")
    
    function_data = tool_call_dict['function']
    name = function_data.get('name', 'unknown')
    arguments = function_data.get('arguments', {})
    
    # Parse arguments if they're in string format
    if isinstance(arguments, str):
        import json
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse arguments JSON: {e}")
    
    function = ToolFunctionCall(name=name, arguments=arguments)
    return ToolCall(function=function)

def create_ollama_tool_call(name: str, arguments: dict) -> 'ToolCall':
    """
    Create a ToolCall dataclass from name and arguments.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        ToolCall: Structured Ollama tool call
    """
    from src.type.tool import ToolCall, ToolFunctionCall
    
    function = ToolFunctionCall(name=name, arguments=arguments)
    return ToolCall(function=function)

def create_claude_tool_call(name: str, arguments: dict, tool_id: str = None) -> 'ClaudeToolCall':
    """
    Create a ClaudeToolCall dataclass from name and arguments.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        tool_id: Optional tool ID (auto-generated if not provided)
        
    Returns:
        ClaudeToolCall: Structured Claude tool call
    """
    from src.type.tool import ClaudeToolCall
    
    if tool_id is None:
        tool_id = f"toolu_{uuid.uuid4().hex[:12]}"
        
    return ClaudeToolCall(
        type="tool_use",
        id=tool_id,
        name=name,
        input=arguments
    )