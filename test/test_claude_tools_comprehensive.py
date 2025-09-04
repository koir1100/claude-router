#!/usr/bin/env python3
"""
Comprehensive test suite for all Claude Code tools through the Claude Router
Tests all 19 supported Claude Code tools to ensure proper format conversion and execution
"""
import requests
import json
import time
import os
import tempfile
from pathlib import Path
import pytest

class ClaudeToolTester:
    def __init__(self, router_url="http://localhost:4000"):
        self.router_url = router_url
        self.base_model = "gpt-oss"
        self.max_tokens = 4000
        
    def send_tool_request(self, tools, user_message, timeout=60):
        """Send a tool request through the Claude Router"""
        payload = {
            "model": self.base_model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": user_message}],
            "tools": tools,
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.router_url}/v1/messages",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=timeout
            )
            
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
            
            # Collect streaming response
            tool_calls = []
            content_parts = []
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_part = line_str[6:]
                        if data_part.strip() == '[DONE]':
                            break
                        
                        try:
                            event_data = json.loads(data_part)
                            
                            if event_data.get('type') == 'content_block_start':
                                block = event_data.get('content_block', {})
                                if block.get('type') == 'tool_use':
                                    tool_calls.append(block)
                            
                            elif event_data.get('type') == 'content_block_delta':
                                delta = event_data.get('delta', {})
                                if delta.get('type') == 'text_delta':
                                    content_parts.append(delta.get('text', ''))
                                    
                        except json.JSONDecodeError:
                            continue
            
            return {
                "success": True,
                "tool_calls": tool_calls,
                "content": ''.join(content_parts),
                "tool_count": len(tool_calls)
            }
            
        except Exception as e:
            return {"error": str(e)}

# Initialize tester
tester = ClaudeToolTester()

def test_router_health():
    """Test that the Claude Router is running and healthy"""
    try:
        response = requests.get(f"{tester.router_url}/health", timeout=5)
        assert response.status_code == 200
        health_data = response.json()
        assert health_data.get("status") == "ok"
        assert health_data.get("model") == "gpt-oss:20b"
        print("✅ Router health check passed")
    except Exception as e:
        pytest.fail(f"Router health check failed: {e}")

def create_claude_tool_schema(name, description, properties, required=None):
    """Helper to create Claude Code tool schema"""
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required or []
        }
    }

# File Operations Tools Tests
def test_write_tool():
    """Test Write tool through router"""
    tool = create_claude_tool_schema(
        "Write",
        "Writes a file to the local filesystem",
        {
            "file_path": {"type": "string"},
            "content": {"type": "string"}
        },
        ["file_path", "content"]
    )
    
    message = "Create a hello world file at /tmp/test_write.txt with the content 'Hello, World!'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Write tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Write tool was not called"
    
    # Check if Write tool was called
    write_calls = [tc for tc in result["tool_calls"] if tc.get("name") == "Write"]
    assert len(write_calls) > 0, "Write tool was not invoked"
    
    print("✅ Write tool test passed")

def test_read_tool():
    """Test Read tool through router"""
    tool = create_claude_tool_schema(
        "Read",
        "Reads a file from the local filesystem",
        {
            "file_path": {"type": "string"},
            "limit": {"type": "number"},
            "offset": {"type": "number"}
        },
        ["file_path"]
    )
    
    message = "Read the contents of /etc/passwd file"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Read tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Read tool was not called"
    
    read_calls = [tc for tc in result["tool_calls"] if tc.get("name") == "Read"]
    assert len(read_calls) > 0, "Read tool was not invoked"
    
    print("✅ Read tool test passed")

def test_edit_tool():
    """Test Edit tool through router"""
    tool = create_claude_tool_schema(
        "Edit",
        "Performs exact string replacements in files",
        {
            "file_path": {"type": "string"},
            "old_string": {"type": "string"},
            "new_string": {"type": "string"},
            "replace_all": {"type": "boolean"}
        },
        ["file_path", "old_string", "new_string"]
    )
    
    message = "Edit /tmp/test.txt to replace 'old text' with 'new text'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Edit tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Edit tool was not called"
    
    print("✅ Edit tool test passed")

def test_multiedit_tool():
    """Test MultiEdit tool through router"""
    tool = create_claude_tool_schema(
        "MultiEdit",
        "Makes multiple edits to a single file in one operation",
        {
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
        ["file_path", "edits"]
    )
    
    message = "Make multiple edits to a Python file: replace all 'print' with 'console.log' and 'def' with 'function'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"MultiEdit tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "MultiEdit tool was not called"
    
    print("✅ MultiEdit tool test passed")

# Execution Tools Tests
def test_bash_tool():
    """Test Bash tool through router"""
    tool = create_claude_tool_schema(
        "Bash",
        "Executes a bash command in a persistent shell session",
        {
            "command": {"type": "string"},
            "description": {"type": "string"},
            "run_in_background": {"type": "boolean"},
            "timeout": {"type": "number"}
        },
        ["command"]
    )
    
    message = "Run the command 'echo Hello from bash' in the terminal"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Bash tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Bash tool was not called"
    
    print("✅ Bash tool test passed")

def test_bashoutput_tool():
    """Test BashOutput tool through router"""
    tool = create_claude_tool_schema(
        "BashOutput",
        "Retrieves output from a running or completed background bash shell",
        {
            "bash_id": {"type": "string"},
            "filter": {"type": "string"}
        },
        ["bash_id"]
    )
    
    message = "Get output from background bash shell with ID 'test-shell-123'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"BashOutput tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "BashOutput tool was not called"
    
    print("✅ BashOutput tool test passed")

def test_killbash_tool():
    """Test KillBash tool through router"""
    tool = create_claude_tool_schema(
        "KillBash",
        "Kills a running background bash shell by its ID",
        {
            "shell_id": {"type": "string"}
        },
        ["shell_id"]
    )
    
    message = "Kill the background bash shell with ID 'test-shell-456'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"KillBash tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "KillBash tool was not called"
    
    print("✅ KillBash tool test passed")

# Search Tools Tests  
def test_glob_tool():
    """Test Glob tool through router"""
    tool = create_claude_tool_schema(
        "Glob",
        "Fast file pattern matching tool",
        {
            "pattern": {"type": "string"},
            "path": {"type": "string"}
        },
        ["pattern"]
    )
    
    message = "Find all Python files in the current directory using pattern '*.py'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Glob tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Glob tool was not called"
    
    print("✅ Glob tool test passed")

def test_grep_tool():
    """Test Grep tool through router"""
    tool = create_claude_tool_schema(
        "Grep",
        "A powerful search tool built on ripgrep",
        {
            "pattern": {"type": "string"},
            "path": {"type": "string"},
            "glob": {"type": "string"},
            "type": {"type": "string"},
            "output_mode": {"type": "string", "enum": ["content", "files_with_matches", "count"]},
            "-i": {"type": "boolean"},
            "-n": {"type": "boolean"},
            "multiline": {"type": "boolean"},
            "head_limit": {"type": "number"}
        },
        ["pattern"]
    )
    
    message = "Search for the word 'function' in all JavaScript files"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Grep tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Grep tool was not called"
    
    print("✅ Grep tool test passed")

# Web Tools Tests
def test_webfetch_tool():
    """Test WebFetch tool through router"""
    tool = create_claude_tool_schema(
        "WebFetch",
        "Fetches content from a specified URL",
        {
            "url": {"type": "string", "format": "uri"},
            "prompt": {"type": "string"}
        },
        ["url", "prompt"]
    )
    
    message = "Fetch the homepage of example.com and summarize its content"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"WebFetch tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "WebFetch tool was not called"
    
    print("✅ WebFetch tool test passed")

def test_websearch_tool():
    """Test WebSearch tool through router"""
    tool = create_claude_tool_schema(
        "WebSearch",
        "Search the web and use results to inform responses",
        {
            "query": {"type": "string"},
            "allowed_domains": {"type": "array", "items": {"type": "string"}},
            "blocked_domains": {"type": "array", "items": {"type": "string"}}
        },
        ["query"]
    )
    
    message = "Search the web for 'Claude AI assistant latest features'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"WebSearch tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "WebSearch tool was not called"
    
    print("✅ WebSearch tool test passed")

# Notebook Tools Tests
def test_notebookedit_tool():
    """Test NotebookEdit tool through router"""
    tool = create_claude_tool_schema(
        "NotebookEdit",
        "Replaces contents of a specific cell in a Jupyter notebook",
        {
            "notebook_path": {"type": "string"},
            "new_source": {"type": "string"},
            "cell_id": {"type": "string"},
            "cell_type": {"type": "string", "enum": ["code", "markdown"]},
            "edit_mode": {"type": "string", "enum": ["replace", "insert", "delete"]}
        },
        ["notebook_path", "new_source"]
    )
    
    message = "Edit the first cell in notebook.ipynb to contain 'print(\"Hello Jupyter\")'"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"NotebookEdit tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "NotebookEdit tool was not called"
    
    print("✅ NotebookEdit tool test passed")

def test_mcp_ide_executecode_tool():
    """Test mcp__ide__executeCode tool through router"""
    tool = create_claude_tool_schema(
        "mcp__ide__executeCode",
        "Execute python code in the Jupyter kernel",
        {
            "code": {"type": "string"}
        },
        ["code"]
    )
    
    message = "Execute the Python code: print('Hello from Jupyter kernel')"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"mcp__ide__executeCode tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "mcp__ide__executeCode tool was not called"
    
    print("✅ mcp__ide__executeCode tool test passed")

# Task Management Tools Tests
def test_todowrite_tool():
    """Test TodoWrite tool through router"""
    tool = create_claude_tool_schema(
        "TodoWrite",
        "Create and manage a structured task list",
        {
            "todos": {
                "type": "array",
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
        ["todos"]
    )
    
    message = "Create a todo list for building a web application with authentication, database, and frontend"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"TodoWrite tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "TodoWrite tool was not called"
    
    print("✅ TodoWrite tool test passed")

def test_task_tool():
    """Test Task tool through router"""
    tool = create_claude_tool_schema(
        "Task",
        "Launch a new agent to handle complex, multi-step tasks autonomously",
        {
            "description": {"type": "string"},
            "prompt": {"type": "string"},
            "subagent_type": {"type": "string"}
        },
        ["description", "prompt", "subagent_type"]
    )
    
    message = "Launch a general-purpose agent to research Python web frameworks and create a comparison"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"Task tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "Task tool was not called"
    
    print("✅ Task tool test passed")

def test_exitplanmode_tool():
    """Test ExitPlanMode tool through router"""
    tool = create_claude_tool_schema(
        "ExitPlanMode",
        "Exit plan mode and present plan for user approval",
        {
            "plan": {"type": "string"}
        },
        ["plan"]
    )
    
    message = "I've finished planning the implementation. Present the plan: 1. Setup database 2. Create API 3. Build frontend"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"ExitPlanMode tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "ExitPlanMode tool was not called"
    
    print("✅ ExitPlanMode tool test passed")

# IDE Integration Tools Tests
def test_mcp_ide_getdiagnostics_tool():
    """Test mcp__ide__getDiagnostics tool through router"""
    tool = create_claude_tool_schema(
        "mcp__ide__getDiagnostics",
        "Get language diagnostics from VS Code",
        {
            "uri": {"type": "string"}
        },
        []
    )
    
    message = "Get diagnostics for the current file to check for errors"
    result = tester.send_tool_request([tool], message)
    
    assert not result.get("error"), f"mcp__ide__getDiagnostics tool failed: {result.get('error')}"
    assert result.get("tool_count") > 0, "mcp__ide__getDiagnostics tool was not called"
    
    print("✅ mcp__ide__getDiagnostics tool test passed")

# Comprehensive test runner
def test_all_tools_comprehensive():
    """Run all tool tests in sequence"""
    print("\n🧪 Running comprehensive Claude Code tools test suite...")
    
    # Test categories
    test_functions = [
        test_router_health,
        test_write_tool,
        test_read_tool, 
        test_edit_tool,
        test_multiedit_tool,
        test_bash_tool,
        test_bashoutput_tool,
        test_killbash_tool,
        test_glob_tool,
        test_grep_tool,
        test_webfetch_tool,
        test_websearch_tool,
        test_notebookedit_tool,
        test_mcp_ide_executecode_tool,
        test_todowrite_tool,
        test_task_tool,
        test_exitplanmode_tool,
        test_mcp_ide_getdiagnostics_tool
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    assert failed == 0, f"{failed} tests failed"

if __name__ == "__main__":
    test_all_tools_comprehensive()