#!/usr/bin/env python3
"""
Test script to directly test Ollama's tool calling with our router
"""
import json
import requests

def test_tool_calling():
    url = "http://localhost:4000/v1/messages"
    
    # Test with a simple file creation request
    payload = {
        "messages": [
            {"role": "user", "content": "Create a file called hello.txt with content 'Hello World!'"}
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
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to write"
                            },
                            "content": {
                                "type": "string", 
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            }
        ]
    }
    
    print("🧪 Testing tool calling with router...")
    print(f"📤 Sending request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        response.raise_for_status()
        
        print("📥 Response:")
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                print(line)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_tool_calling()