#!/usr/bin/env python3
"""
File Operations Tools Test Suite
Tests: Write, Read, Edit, MultiEdit
"""
import requests
import json
import tempfile
import os
from pathlib import Path

class FileOperationsTest:
    def __init__(self, router_url="http://localhost:4000"):
        self.router_url = router_url
        self.test_dir = tempfile.mkdtemp()
        
    def send_request(self, tools, message):
        payload = {
            "model": "gpt-oss",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": message}],
            "tools": tools,
            "stream": True
        }
        
        response = requests.post(
            f"{self.router_url}/v1/messages",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        tool_calls = []
        for line in response.iter_lines():
            if line and line.decode('utf-8').startswith('data: '):
                try:
                    data = json.loads(line.decode('utf-8')[6:])
                    if data.get('type') == 'content_block_start':
                        block = data.get('content_block', {})
                        if block.get('type') == 'tool_use':
                            tool_calls.append(block)
                except json.JSONDecodeError:
                    continue
                    
        return tool_calls

def test_write_read_cycle():
    """Test Write then Read file operations"""
    tester = FileOperationsTest()
    test_file = os.path.join(tester.test_dir, "test_write_read.txt")
    
    # Write tool schema
    write_tool = {
        "name": "Write",
        "description": "Writes a file to the local filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["file_path", "content"]
        }
    }
    
    # Read tool schema
    read_tool = {
        "name": "Read", 
        "description": "Reads a file from the local filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"}
            },
            "required": ["file_path"]
        }
    }
    
    # Test Write
    write_message = f"Write a file at {test_file} with content 'Hello File Operations Test!'"
    write_calls = tester.send_request([write_tool], write_message)
    
    assert len(write_calls) > 0, "Write tool not called"
    assert write_calls[0]["name"] == "Write", "Wrong tool called"
    print("✅ Write tool call successful")
    
    # Test Read
    read_message = f"Read the contents of file {test_file}"
    read_calls = tester.send_request([read_tool], read_message)
    
    assert len(read_calls) > 0, "Read tool not called"
    assert read_calls[0]["name"] == "Read", "Wrong tool called"
    print("✅ Read tool call successful")

def test_edit_operations():
    """Test Edit tool for string replacement"""
    tester = FileOperationsTest()
    
    edit_tool = {
        "name": "Edit",
        "description": "Performs exact string replacements in files",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
                "replace_all": {"type": "boolean"}
            },
            "required": ["file_path", "old_string", "new_string"]
        }
    }
    
    message = "Edit the file config.py to replace 'DEBUG = True' with 'DEBUG = False'"
    calls = tester.send_request([edit_tool], message)
    
    assert len(calls) > 0, "Edit tool not called"
    assert calls[0]["name"] == "Edit", "Wrong tool called"
    print("✅ Edit tool call successful")

def test_multiedit_operations():
    """Test MultiEdit tool for multiple replacements"""
    tester = FileOperationsTest()
    
    multiedit_tool = {
        "name": "MultiEdit",
        "description": "Makes multiple edits to a single file in one operation",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "edits": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "old_string": {"type": "string"},
                            "new_string": {"type": "string"},
                            "replace_all": {"type": "boolean"}
                        },
                        "required": ["old_string", "new_string"]
                    }
                }
            },
            "required": ["file_path", "edits"]
        }
    }
    
    message = "Make multiple edits to app.py: replace 'localhost' with '0.0.0.0' and 'port=5000' with 'port=8080'"
    calls = tester.send_request([multiedit_tool], message)
    
    assert len(calls) > 0, "MultiEdit tool not called"
    assert calls[0]["name"] == "MultiEdit", "Wrong tool called"
    print("✅ MultiEdit tool call successful")

def test_file_operations_comprehensive():
    """Run all file operations tests"""
    print("🧪 Testing File Operations Tools...")
    
    test_write_read_cycle()
    test_edit_operations() 
    test_multiedit_operations()
    
    print("✅ All file operations tests passed!")

if __name__ == "__main__":
    test_file_operations_comprehensive()