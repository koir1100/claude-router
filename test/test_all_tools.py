#!/usr/bin/env python3
"""
Test all Claude Code tools through the router
"""
import json
import requests

def test_comprehensive_tools():
    url = "http://localhost:4000/v1/messages"
    
    # Simulate Claude Code sending comprehensive tools
    payload = {
        "messages": [
            {"role": "user", "content": "Create a test file, then read it, and list the current directory"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "Write",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "Read",
                    "description": "Read content from a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "LS", 
                    "description": "List files and directories",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "Bash",
                    "description": "Execute bash commands",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "command": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
    }
    
    print("🧪 Testing comprehensive Claude Code tools...")
    print(f"📤 Sending request with {len(payload['tools'])} tools")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        response.raise_for_status()
        
        print("📥 Response stream:")
        for line in response.iter_lines(decode_unicode=True):
            if line.strip() and 'data:' in line:
                try:
                    data = json.loads(line.split('data: ')[1])
                    if data.get('type') == 'content_block_start' and 'tool_use' in str(data):
                        tool_info = data.get('content_block', {})
                        print(f"🛠️  Tool used: {tool_info.get('name')} - {tool_info.get('input')}")
                    elif data.get('type') == 'content_block_start' and 'tool_result' in str(data):
                        result = data.get('content_block', {}).get('content', '')
                        print(f"✅ Tool result: {result}")
                except:
                    pass
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_comprehensive_tools()