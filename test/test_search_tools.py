#!/usr/bin/env python3
"""
Search Tools Test Suite
Tests: Glob, Grep
"""
import requests
import json

class SearchToolsTest:
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

def test_glob_pattern_matching():
    """Test Glob tool for file pattern matching"""
    tester = SearchToolsTest()
    
    glob_tool = {
        "name": "Glob",
        "description": "Fast file pattern matching tool",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string"}
            },
            "required": ["pattern"]
        }
    }
    
    message = "Find all Python files using the pattern '*.py'"
    calls = tester.send_request([glob_tool], message)
    
    assert len(calls) > 0, "Glob tool not called"
    assert calls[0]["name"] == "Glob", "Wrong tool called"
    
    # Verify pattern parameter is present
    tool_input = calls[0].get("input", {})
    assert "pattern" in tool_input, "Pattern parameter missing"
    
    print("✅ Glob pattern matching test successful")

def test_glob_with_path():
    """Test Glob tool with specific path"""
    tester = SearchToolsTest()
    
    glob_tool = {
        "name": "Glob",
        "description": "Fast file pattern matching tool",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string"}
            },
            "required": ["pattern"]
        }
    }
    
    message = "Find all JavaScript files in the src directory using pattern '**/*.js'"
    calls = tester.send_request([glob_tool], message)
    
    assert len(calls) > 0, "Glob with path tool not called"
    assert calls[0]["name"] == "Glob", "Wrong tool called"
    
    print("✅ Glob with path test successful")

def test_glob_recursive_patterns():
    """Test Glob tool with recursive patterns"""
    tester = SearchToolsTest()
    
    glob_tool = {
        "name": "Glob",
        "description": "Fast file pattern matching tool",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string"}
            },
            "required": ["pattern"]
        }
    }
    
    message = "Find all TypeScript files recursively using pattern '**/*.{ts,tsx}'"
    calls = tester.send_request([glob_tool], message)
    
    assert len(calls) > 0, "Glob recursive tool not called"
    assert calls[0]["name"] == "Glob", "Wrong tool called"
    
    print("✅ Glob recursive patterns test successful")

def test_grep_content_search():
    """Test Grep tool for content searching"""
    tester = SearchToolsTest()
    
    grep_tool = {
        "name": "Grep",
        "description": "A powerful search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "required": ["pattern"]
        }
    }
    
    message = "Search for the word 'function' in all files"
    calls = tester.send_request([grep_tool], message)
    
    assert len(calls) > 0, "Grep tool not called"
    assert calls[0]["name"] == "Grep", "Wrong tool called"
    
    # Verify pattern parameter is present
    tool_input = calls[0].get("input", {})
    assert "pattern" in tool_input, "Pattern parameter missing"
    
    print("✅ Grep content search test successful")

def test_grep_with_file_type():
    """Test Grep tool with file type filtering"""
    tester = SearchToolsTest()
    
    grep_tool = {
        "name": "Grep",
        "description": "A powerful search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "required": ["pattern"]
        }
    }
    
    message = "Search for 'import' statements in Python files only"
    calls = tester.send_request([grep_tool], message)
    
    assert len(calls) > 0, "Grep file type tool not called"
    assert calls[0]["name"] == "Grep", "Wrong tool called"
    
    print("✅ Grep with file type test successful")

def test_grep_case_insensitive():
    """Test Grep tool with case insensitive search"""
    tester = SearchToolsTest()
    
    grep_tool = {
        "name": "Grep",
        "description": "A powerful search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "required": ["pattern"]
        }
    }
    
    message = "Search for 'ERROR' or 'error' (case insensitive) in log files"
    calls = tester.send_request([grep_tool], message)
    
    assert len(calls) > 0, "Grep case insensitive tool not called"
    assert calls[0]["name"] == "Grep", "Wrong tool called"
    
    print("✅ Grep case insensitive test successful")

def test_grep_with_line_numbers():
    """Test Grep tool with line number display"""
    tester = SearchToolsTest()
    
    grep_tool = {
        "name": "Grep",
        "description": "A powerful search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "required": ["pattern"]
        }
    }
    
    message = "Search for 'TODO' comments and show line numbers"
    calls = tester.send_request([grep_tool], message)
    
    assert len(calls) > 0, "Grep line numbers tool not called"
    assert calls[0]["name"] == "Grep", "Wrong tool called"
    
    print("✅ Grep with line numbers test successful")

def test_grep_output_modes():
    """Test Grep tool with different output modes"""
    tester = SearchToolsTest()
    
    grep_tool = {
        "name": "Grep",
        "description": "A powerful search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "required": ["pattern"]
        }
    }
    
    message = "Count how many times 'class' appears in all files"
    calls = tester.send_request([grep_tool], message)
    
    assert len(calls) > 0, "Grep output modes tool not called"
    assert calls[0]["name"] == "Grep", "Wrong tool called"
    
    print("✅ Grep output modes test successful")

def test_grep_multiline_search():
    """Test Grep tool with multiline pattern matching"""
    tester = SearchToolsTest()
    
    grep_tool = {
        "name": "Grep",
        "description": "A powerful search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "required": ["pattern"]
        }
    }
    
    message = "Search for function definitions that span multiple lines"
    calls = tester.send_request([grep_tool], message)
    
    assert len(calls) > 0, "Grep multiline tool not called"
    assert calls[0]["name"] == "Grep", "Wrong tool called"
    
    print("✅ Grep multiline search test successful")

def test_search_tools_workflow():
    """Test combined search workflow: Glob to find files, then Grep to search content"""
    tester = SearchToolsTest()
    
    all_tools = [
        {
            "name": "Glob",
            "description": "Fast file pattern matching tool",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"}
                },
                "required": ["pattern"]
            }
        },
        {
            "name": "Grep",
            "description": "A powerful search tool built on ripgrep",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "glob": {"type": "string"},
                    "output_mode": {"type": "string", "enum": ["content", "files_with_matches", "count"]}
                },
                "required": ["pattern"]
            }
        }
    ]
    
    message = "Find all Python test files and then search for assertion statements in them"
    calls = tester.send_request(all_tools, message)
    
    assert len(calls) > 0, "No search tools called in workflow"
    
    # Should call at least one search tool
    tool_names = [call["name"] for call in calls]
    search_tools = {"Glob", "Grep"}
    called_tools = set(tool_names) & search_tools
    
    assert len(called_tools) > 0, f"No search tools called. Called: {tool_names}"
    
    print(f"✅ Search workflow test successful - Called: {list(called_tools)}")

def test_search_tools_comprehensive():
    """Run all search tools tests"""
    print("🧪 Testing Search Tools...")
    
    test_glob_pattern_matching()
    test_glob_with_path()
    test_glob_recursive_patterns()
    test_grep_content_search()
    test_grep_with_file_type()
    test_grep_case_insensitive()
    test_grep_with_line_numbers()
    test_grep_output_modes()
    test_grep_multiline_search()
    test_search_tools_workflow()
    
    print("✅ All search tools tests passed!")

if __name__ == "__main__":
    test_search_tools_comprehensive()