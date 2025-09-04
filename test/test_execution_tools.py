#!/usr/bin/env python3
"""
Execution Tools Test Suite
Tests: Bash, BashOutput, KillBash
"""
import requests
import json
import time

class ExecutionToolsTest:
    def __init__(self, router_url="http://localhost:4000"):
        self.router_url = router_url
        
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

def test_bash_command_execution():
    """Test Bash tool for command execution"""
    tester = ExecutionToolsTest()
    
    bash_tool = {
        "name": "Bash",
        "description": "Executes a bash command in a persistent shell session",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "description": {"type": "string"},
                "run_in_background": {"type": "boolean"},
                "timeout": {"type": "number"}
            },
            "required": ["command"]
        }
    }
    
    message = "Run the bash command 'echo \"Hello from bash execution test\"'"
    calls = tester.send_request([bash_tool], message)
    
    assert len(calls) > 0, "Bash tool not called"
    assert calls[0]["name"] == "Bash", "Wrong tool called"
    
    # Verify command parameter is present
    tool_input = calls[0].get("input", {})
    assert "command" in tool_input, "Command parameter missing"
    
    print("✅ Bash tool call successful")

def test_bash_background_execution():
    """Test Bash tool for background command execution"""
    tester = ExecutionToolsTest()
    
    bash_tool = {
        "name": "Bash",
        "description": "Executes a bash command in a persistent shell session",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "description": {"type": "string"},
                "run_in_background": {"type": "boolean"},
                "timeout": {"type": "number"}
            },
            "required": ["command"]
        }
    }
    
    message = "Run 'sleep 10' in the background"
    calls = tester.send_request([bash_tool], message)
    
    assert len(calls) > 0, "Bash background tool not called"
    assert calls[0]["name"] == "Bash", "Wrong tool called"
    
    print("✅ Bash background execution test successful")

def test_bash_with_timeout():
    """Test Bash tool with timeout parameter"""
    tester = ExecutionToolsTest()
    
    bash_tool = {
        "name": "Bash",
        "description": "Executes a bash command in a persistent shell session",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "description": {"type": "string"},
                "run_in_background": {"type": "boolean"},
                "timeout": {"type": "number"}
            },
            "required": ["command"]
        }
    }
    
    message = "Run 'ls -la' with a timeout of 5 seconds"
    calls = tester.send_request([bash_tool], message)
    
    assert len(calls) > 0, "Bash timeout tool not called"
    assert calls[0]["name"] == "Bash", "Wrong tool called"
    
    print("✅ Bash timeout test successful")

def test_bashoutput_retrieval():
    """Test BashOutput tool for retrieving command output"""
    tester = ExecutionToolsTest()
    
    bashoutput_tool = {
        "name": "BashOutput",
        "description": "Retrieves output from a running or completed background bash shell",
        "input_schema": {
            "type": "object",
            "properties": {
                "bash_id": {"type": "string"},
                "filter": {"type": "string"}
            },
            "required": ["bash_id"]
        }
    }
    
    message = "Get the output from bash shell with ID 'test-shell-123'"
    calls = tester.send_request([bashoutput_tool], message)
    
    assert len(calls) > 0, "BashOutput tool not called"
    assert calls[0]["name"] == "BashOutput", "Wrong tool called"
    
    # Verify bash_id parameter is present
    tool_input = calls[0].get("input", {})
    assert "bash_id" in tool_input, "bash_id parameter missing"
    
    print("✅ BashOutput tool call successful")

def test_bashoutput_with_filter():
    """Test BashOutput tool with regex filter"""
    tester = ExecutionToolsTest()
    
    bashoutput_tool = {
        "name": "BashOutput",
        "description": "Retrieves output from a running or completed background bash shell",
        "input_schema": {
            "type": "object",
            "properties": {
                "bash_id": {"type": "string"},
                "filter": {"type": "string"}
            },
            "required": ["bash_id"]
        }
    }
    
    message = "Get output from shell 'log-shell' filtering only lines containing 'ERROR'"
    calls = tester.send_request([bashoutput_tool], message)
    
    assert len(calls) > 0, "BashOutput filter tool not called"
    assert calls[0]["name"] == "BashOutput", "Wrong tool called"
    
    print("✅ BashOutput filter test successful")

def test_killbash_termination():
    """Test KillBash tool for terminating background shells"""
    tester = ExecutionToolsTest()
    
    killbash_tool = {
        "name": "KillBash",
        "description": "Kills a running background bash shell by its ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "shell_id": {"type": "string"}
            },
            "required": ["shell_id"]
        }
    }
    
    message = "Kill the background bash shell with ID 'long-running-task'"
    calls = tester.send_request([killbash_tool], message)
    
    assert len(calls) > 0, "KillBash tool not called"
    assert calls[0]["name"] == "KillBash", "Wrong tool called"
    
    # Verify shell_id parameter is present
    tool_input = calls[0].get("input", {})
    assert "shell_id" in tool_input, "shell_id parameter missing"
    
    print("✅ KillBash tool call successful")

def test_execution_tools_workflow():
    """Test complete execution workflow: Bash -> BashOutput -> KillBash"""
    tester = ExecutionToolsTest()
    
    all_tools = [
        {
            "name": "Bash",
            "description": "Executes a bash command in a persistent shell session",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "run_in_background": {"type": "boolean"}
                },
                "required": ["command"]
            }
        },
        {
            "name": "BashOutput",
            "description": "Retrieves output from a running background bash shell",
            "input_schema": {
                "type": "object",
                "properties": {
                    "bash_id": {"type": "string"}
                },
                "required": ["bash_id"]
            }
        },
        {
            "name": "KillBash",
            "description": "Kills a running background bash shell",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shell_id": {"type": "string"}
                },
                "required": ["shell_id"]
            }
        }
    ]
    
    message = "Start a background process to monitor system logs, then check its output, and finally terminate it"
    calls = tester.send_request(all_tools, message)
    
    assert len(calls) > 0, "No execution tools called in workflow"
    
    # Should call at least one execution tool
    tool_names = [call["name"] for call in calls]
    execution_tools = {"Bash", "BashOutput", "KillBash"}
    called_tools = set(tool_names) & execution_tools
    
    assert len(called_tools) > 0, f"No execution tools called. Called: {tool_names}"
    
    print(f"✅ Execution workflow test successful - Called: {list(called_tools)}")

def test_execution_tools_comprehensive():
    """Run all execution tools tests"""
    print("🧪 Testing Execution Tools...")
    
    test_bash_command_execution()
    test_bash_background_execution()
    test_bash_with_timeout()
    test_bashoutput_retrieval()
    test_bashoutput_with_filter()
    test_killbash_termination()
    test_execution_tools_workflow()
    
    print("✅ All execution tools tests passed!")

if __name__ == "__main__":
    test_execution_tools_comprehensive()