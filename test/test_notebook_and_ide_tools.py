#!/usr/bin/env python3
"""
Notebook and IDE Tools Test Suite
Tests: NotebookEdit, mcp__ide__executeCode, mcp__ide__getDiagnostics
"""
import requests
import json
import tempfile
import os

class NotebookAndIDEToolsTest:
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

def test_notebookedit_basic():
    """Test NotebookEdit tool for basic cell replacement"""
    tester = NotebookAndIDEToolsTest()
    
    notebookedit_tool = {
        "name": "NotebookEdit",
        "description": "Completely replaces the contents of a specific cell in a Jupyter notebook",
        "input_schema": {
            "type": "object",
            "properties": {
                "notebook_path": {"type": "string"},
                "new_source": {"type": "string"},
                "cell_id": {"type": "string"},
                "cell_type": {"type": "string", "enum": ["code", "markdown"]},
                "edit_mode": {"type": "string", "enum": ["replace", "insert", "delete"]}
            },
            "required": ["notebook_path", "new_source"]
        }
    }
    
    message = "Edit the first cell in notebook.ipynb to contain the code 'print(\"Hello Jupyter!\")'"
    calls = tester.send_request([notebookedit_tool], message)
    
    assert len(calls) > 0, "NotebookEdit tool not called"
    assert calls[0]["name"] == "NotebookEdit", "Wrong tool called"
    
    # Verify required parameters are present
    tool_input = calls[0].get("input", {})
    assert "notebook_path" in tool_input, "notebook_path parameter missing"
    assert "new_source" in tool_input, "new_source parameter missing"
    
    print("✅ NotebookEdit basic test successful")

def test_notebookedit_markdown_cell():
    """Test NotebookEdit tool for markdown cell editing"""
    tester = NotebookAndIDEToolsTest()
    
    notebookedit_tool = {
        "name": "NotebookEdit",
        "description": "Completely replaces the contents of a specific cell in a Jupyter notebook",
        "input_schema": {
            "type": "object",
            "properties": {
                "notebook_path": {"type": "string"},
                "new_source": {"type": "string"},
                "cell_id": {"type": "string"},
                "cell_type": {"type": "string", "enum": ["code", "markdown"]},
                "edit_mode": {"type": "string", "enum": ["replace", "insert", "delete"]}
            },
            "required": ["notebook_path", "new_source"]
        }
    }
    
    message = "Create a markdown cell in analysis.ipynb with title '# Data Analysis Results' and description"
    calls = tester.send_request([notebookedit_tool], message)
    
    assert len(calls) > 0, "NotebookEdit markdown tool not called"
    assert calls[0]["name"] == "NotebookEdit", "Wrong tool called"
    
    print("✅ NotebookEdit markdown cell test successful")

def test_notebookedit_insert_cell():
    """Test NotebookEdit tool for inserting new cells"""
    tester = NotebookAndIDEToolsTest()
    
    notebookedit_tool = {
        "name": "NotebookEdit",
        "description": "Completely replaces the contents of a specific cell in a Jupyter notebook",
        "input_schema": {
            "type": "object",
            "properties": {
                "notebook_path": {"type": "string"},
                "new_source": {"type": "string"},
                "cell_id": {"type": "string"},
                "cell_type": {"type": "string", "enum": ["code", "markdown"]},
                "edit_mode": {"type": "string", "enum": ["replace", "insert", "delete"]}
            },
            "required": ["notebook_path", "new_source"]
        }
    }
    
    message = "Insert a new code cell after cell 3 in data_processing.ipynb with pandas import statement"
    calls = tester.send_request([notebookedit_tool], message)
    
    assert len(calls) > 0, "NotebookEdit insert tool not called"
    assert calls[0]["name"] == "NotebookEdit", "Wrong tool called"
    
    print("✅ NotebookEdit insert cell test successful")

def test_notebookedit_delete_cell():
    """Test NotebookEdit tool for deleting cells"""
    tester = NotebookAndIDEToolsTest()
    
    notebookedit_tool = {
        "name": "NotebookEdit",
        "description": "Completely replaces the contents of a specific cell in a Jupyter notebook",
        "input_schema": {
            "type": "object",
            "properties": {
                "notebook_path": {"type": "string"},
                "new_source": {"type": "string"},
                "cell_id": {"type": "string"},
                "cell_type": {"type": "string", "enum": ["code", "markdown"]},
                "edit_mode": {"type": "string", "enum": ["replace", "insert", "delete"]}
            },
            "required": ["notebook_path", "new_source"]
        }
    }
    
    message = "Delete the empty cell number 5 from experiment.ipynb"
    calls = tester.send_request([notebookedit_tool], message)
    
    assert len(calls) > 0, "NotebookEdit delete tool not called"
    assert calls[0]["name"] == "NotebookEdit", "Wrong tool called"
    
    print("✅ NotebookEdit delete cell test successful")

def test_mcp_ide_executecode_basic():
    """Test mcp__ide__executeCode tool for basic code execution"""
    tester = NotebookAndIDEToolsTest()
    
    executecode_tool = {
        "name": "mcp__ide__executeCode",
        "description": "Execute python code in the Jupyter kernel for the current notebook file",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"}
            },
            "required": ["code"]
        }
    }
    
    message = "Execute the Python code: print('Hello from Jupyter kernel!')"
    calls = tester.send_request([executecode_tool], message)
    
    assert len(calls) > 0, "mcp__ide__executeCode tool not called"
    assert calls[0]["name"] == "mcp__ide__executeCode", "Wrong tool called"
    
    # Verify code parameter is present
    tool_input = calls[0].get("input", {})
    assert "code" in tool_input, "code parameter missing"
    
    print("✅ mcp__ide__executeCode basic test successful")

def test_mcp_ide_executecode_calculations():
    """Test mcp__ide__executeCode tool for mathematical calculations"""
    tester = NotebookAndIDEToolsTest()
    
    executecode_tool = {
        "name": "mcp__ide__executeCode",
        "description": "Execute python code in the Jupyter kernel for the current notebook file",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"}
            },
            "required": ["code"]
        }
    }
    
    message = "Calculate the mean of the list [1, 2, 3, 4, 5] using Python"
    calls = tester.send_request([executecode_tool], message)
    
    assert len(calls) > 0, "mcp__ide__executeCode calculations tool not called"
    assert calls[0]["name"] == "mcp__ide__executeCode", "Wrong tool called"
    
    print("✅ mcp__ide__executeCode calculations test successful")

def test_mcp_ide_executecode_data_analysis():
    """Test mcp__ide__executeCode tool for data analysis tasks"""
    tester = NotebookAndIDEToolsTest()
    
    executecode_tool = {
        "name": "mcp__ide__executeCode",
        "description": "Execute python code in the Jupyter kernel for the current notebook file",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"}
            },
            "required": ["code"]
        }
    }
    
    message = "Create a simple pandas DataFrame with columns 'name' and 'age' and display it"
    calls = tester.send_request([executecode_tool], message)
    
    assert len(calls) > 0, "mcp__ide__executeCode data analysis tool not called"
    assert calls[0]["name"] == "mcp__ide__executeCode", "Wrong tool called"
    
    print("✅ mcp__ide__executeCode data analysis test successful")

def test_mcp_ide_executecode_plotting():
    """Test mcp__ide__executeCode tool for creating plots"""
    tester = NotebookAndIDEToolsTest()
    
    executecode_tool = {
        "name": "mcp__ide__executeCode",
        "description": "Execute python code in the Jupyter kernel for the current notebook file",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"}
            },
            "required": ["code"]
        }
    }
    
    message = "Create a simple line plot using matplotlib with x values [1,2,3,4] and y values [1,4,9,16]"
    calls = tester.send_request([executecode_tool], message)
    
    assert len(calls) > 0, "mcp__ide__executeCode plotting tool not called"
    assert calls[0]["name"] == "mcp__ide__executeCode", "Wrong tool called"
    
    print("✅ mcp__ide__executeCode plotting test successful")

def test_mcp_ide_getdiagnostics_basic():
    """Test mcp__ide__getDiagnostics tool for getting diagnostics"""
    tester = NotebookAndIDEToolsTest()
    
    getdiagnostics_tool = {
        "name": "mcp__ide__getDiagnostics",
        "description": "Get language diagnostics from VS Code",
        "input_schema": {
            "type": "object",
            "properties": {
                "uri": {"type": "string"}
            },
            "required": []
        }
    }
    
    message = "Check for any errors or warnings in the current file"
    calls = tester.send_request([getdiagnostics_tool], message)
    
    assert len(calls) > 0, "mcp__ide__getDiagnostics tool not called"
    assert calls[0]["name"] == "mcp__ide__getDiagnostics", "Wrong tool called"
    
    print("✅ mcp__ide__getDiagnostics basic test successful")

def test_mcp_ide_getdiagnostics_specific_file():
    """Test mcp__ide__getDiagnostics tool for specific file diagnostics"""
    tester = NotebookAndIDEToolsTest()
    
    getdiagnostics_tool = {
        "name": "mcp__ide__getDiagnostics",
        "description": "Get language diagnostics from VS Code",
        "input_schema": {
            "type": "object",
            "properties": {
                "uri": {"type": "string"}
            },
            "required": []
        }
    }
    
    message = "Get diagnostics for the file main.py to check for syntax errors"
    calls = tester.send_request([getdiagnostics_tool], message)
    
    assert len(calls) > 0, "mcp__ide__getDiagnostics specific file tool not called"
    assert calls[0]["name"] == "mcp__ide__getDiagnostics", "Wrong tool called"
    
    print("✅ mcp__ide__getDiagnostics specific file test successful")

def test_notebook_workflow():
    """Test complete notebook workflow: Edit cells, execute code, check diagnostics"""
    tester = NotebookAndIDEToolsTest()
    
    all_tools = [
        {
            "name": "NotebookEdit",
            "description": "Edit Jupyter notebook cells",
            "input_schema": {
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string"},
                    "new_source": {"type": "string"}
                },
                "required": ["notebook_path", "new_source"]
            }
        },
        {
            "name": "mcp__ide__executeCode",
            "description": "Execute python code in Jupyter kernel",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "mcp__ide__getDiagnostics",
            "description": "Get language diagnostics",
            "input_schema": {
                "type": "object",
                "properties": {
                    "uri": {"type": "string"}
                },
                "required": []
            }
        }
    ]
    
    message = "Create a new notebook cell with data analysis code, execute it to test, and then check for any diagnostics"
    calls = tester.send_request(all_tools, message)
    
    assert len(calls) > 0, "No notebook/IDE tools called in workflow"
    
    # Should call at least one notebook/IDE tool
    tool_names = [call["name"] for call in calls]
    notebook_ide_tools = {"NotebookEdit", "mcp__ide__executeCode", "mcp__ide__getDiagnostics"}
    called_tools = set(tool_names) & notebook_ide_tools
    
    assert len(called_tools) > 0, f"No notebook/IDE tools called. Called: {tool_names}"
    
    print(f"✅ Notebook workflow test successful - Called: {list(called_tools)}")

def test_notebook_and_ide_tools_comprehensive():
    """Run all notebook and IDE tools tests"""
    print("🧪 Testing Notebook and IDE Tools...")
    
    test_notebookedit_basic()
    test_notebookedit_markdown_cell()
    test_notebookedit_insert_cell()
    test_notebookedit_delete_cell()
    test_mcp_ide_executecode_basic()
    test_mcp_ide_executecode_calculations()
    test_mcp_ide_executecode_data_analysis()
    test_mcp_ide_executecode_plotting()
    test_mcp_ide_getdiagnostics_basic()
    test_mcp_ide_getdiagnostics_specific_file()
    test_notebook_workflow()
    
    print("✅ All notebook and IDE tools tests passed!")

if __name__ == "__main__":
    test_notebook_and_ide_tools_comprehensive()