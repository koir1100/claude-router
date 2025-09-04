#!/usr/bin/env python3
"""
Test TodoWrite tool flow through Claude Router
Tests the complete flow: Claude Code -> Router -> Ollama -> Router -> Claude Code
"""
import requests
import json
import time

def test_todowrite_through_router():
    """Test TodoWrite tool calling through the Claude Router"""
    
    # Claude Code message that triggers TodoWrite
    test_message = {
        "model": "gpt-oss",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user", 
                "content": "I need to implement a complete user authentication system for my web application. This should include user registration with email validation, secure login with JWT tokens, password reset functionality, user profile management, and role-based access control. Make sure to also add proper error handling, input validation, database integration, and comprehensive unit tests. Please plan this out step by step and execute each part systematically."
            }
        ],
        "tools": [
            {
                "name": "TodoWrite",
                "description": "Use this tool to create and manage a structured task list for your current coding session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "todos": {
                            "type": "array",
                            "description": "The updated todo list",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"},
                                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                                    "activeForm": {"type": "string"}
                                },
                                "required": ["content", "status", "activeForm"]
                            }
                        }
                    },
                    "required": ["todos"]
                }
            }
        ],
        "stream": True
    }
    
    print("🧪 Testing TodoWrite through Claude Router...")
    print("📝 Sending complex user message that should trigger TodoWrite...")
    
    # Send request to router
    try:
        response = requests.post(
            "http://localhost:4000/v1/messages",
            json=test_message,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=60
        )
        
        print(f"📡 Router Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Router returned error: {response.text}")
            return False
            
        # Collect streaming response
        tool_calls = []
        content_parts = []
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_part = line_str[6:]  # Remove 'data: '
                    if data_part.strip() == '[DONE]':
                        break
                        
                    try:
                        event_data = json.loads(data_part)
                        
                        # Check for tool calls
                        if event_data.get('type') == 'content_block_start':
                            block = event_data.get('content_block', {})
                            if block.get('type') == 'tool_use':
                                tool_calls.append(block)
                                print(f"🔧 Tool Call Detected: {block.get('name')}")
                        
                        # Check for content
                        elif event_data.get('type') == 'content_block_delta':
                            delta = event_data.get('delta', {})
                            if delta.get('type') == 'text_delta':
                                content_parts.append(delta.get('text', ''))
                        
                        elif event_data.get('type') == 'content_block_delta' and event_data.get('delta', {}).get('type') == 'input_json_delta':
                            # Tool input streaming
                            partial_json = event_data.get('delta', {}).get('partial_json', '')
                            print(f"🔧 Tool Input Stream: {partial_json[:100]}...")
                            
                    except json.JSONDecodeError:
                        continue
        
        print(f"\n📊 Test Results:")
        print(f"   Tool Calls Found: {len(tool_calls)}")
        print(f"   Content Blocks: {len(content_parts)}")
        
        # Verify TodoWrite was called
        todowrite_found = any(tool.get('name') == 'TodoWrite' for tool in tool_calls)
        
        if todowrite_found:
            print("✅ TodoWrite tool was successfully called through the router!")
            
            # Print tool call details
            for tool in tool_calls:
                if tool.get('name') == 'TodoWrite':
                    print(f"📋 TodoWrite Input:")
                    print(f"   Tool ID: {tool.get('id')}")
                    input_data = tool.get('input', {})
                    if 'todos' in input_data:
                        todos = input_data['todos']
                        print(f"   Todo Count: {len(todos)}")
                        for i, todo in enumerate(todos[:3]):  # Show first 3
                            print(f"   [{i+1}] {todo.get('content', '')[:50]}...")
            
            return True
        else:
            print("❌ TodoWrite tool was not called")
            print(f"   Available tools: {[t.get('name') for t in tool_calls]}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_todowrite_through_router()
    exit(0 if success else 1)