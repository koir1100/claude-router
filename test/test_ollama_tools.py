#!/usr/bin/env python3
"""
Test Ollama tool calling directly to see if gpt-oss:20b supports it
"""
import json
import requests

def test_ollama_direct():
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "gpt-oss:20b",
        "messages": [
            {"role": "user", "content": "Create a file called test.txt with content 'Hello from Ollama tools!'"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Create a text file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["filename", "content"]
                    }
                }
            }
        ],
        "stream": False
    }
    
    print("🧪 Testing Ollama direct tool calling...")
    print(f"🔗 URL: {url}")
    print(f"📤 Model: {payload['model']}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"📥 Response: {json.dumps(result, indent=2)}")
        
        message = result.get("message", {})
        if "tool_calls" in message:
            print("✅ Tool calls supported!")
            print(f"🛠️  Tool calls: {message['tool_calls']}")
        else:
            print("❌ No tool calls found in response")
            print(f"💬 Content: {message.get('content', 'No content')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ollama_direct()