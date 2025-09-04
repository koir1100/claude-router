#!/usr/bin/env python3
"""
Task Management Tools Test Suite
Tests: TodoWrite, Task, ExitPlanMode
"""
import requests
import json

class TaskManagementToolsTest:
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
            timeout=45  # Longer timeout for complex planning tasks
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

def test_todowrite_basic_planning():
    """Test TodoWrite tool for basic task planning"""
    tester = TaskManagementToolsTest()
    
    todowrite_tool = {
        "name": "TodoWrite",
        "description": "Create and manage a structured task list for your current coding session",
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
    
    message = "Create a todo list for building a simple web application with authentication and database"
    calls = tester.send_request([todowrite_tool], message)
    
    assert len(calls) > 0, "TodoWrite tool not called"
    assert calls[0]["name"] == "TodoWrite", "Wrong tool called"
    
    # Verify todos parameter is present
    tool_input = calls[0].get("input", {})
    assert "todos" in tool_input, "todos parameter missing"
    
    print("✅ TodoWrite basic planning test successful")

def test_todowrite_complex_project():
    """Test TodoWrite tool for complex multi-step project planning"""
    tester = TaskManagementToolsTest()
    
    todowrite_tool = {
        "name": "TodoWrite",
        "description": "Create and manage a structured task list for your current coding session",
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
    
    message = "Plan a complete e-commerce platform with user management, product catalog, shopping cart, payment integration, order management, and admin dashboard. Break this down into detailed implementation steps."
    calls = tester.send_request([todowrite_tool], message)
    
    assert len(calls) > 0, "TodoWrite complex project tool not called"
    assert calls[0]["name"] == "TodoWrite", "Wrong tool called"
    
    print("✅ TodoWrite complex project test successful")

def test_todowrite_task_status_management():
    """Test TodoWrite tool for managing task statuses"""
    tester = TaskManagementToolsTest()
    
    todowrite_tool = {
        "name": "TodoWrite",
        "description": "Create and manage a structured task list for your current coding session",
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
    
    message = "Update my todo list to mark 'Setup database' as completed, 'Create user auth' as in progress, and add a new pending task 'Write unit tests'"
    calls = tester.send_request([todowrite_tool], message)
    
    assert len(calls) > 0, "TodoWrite status management tool not called"
    assert calls[0]["name"] == "TodoWrite", "Wrong tool called"
    
    print("✅ TodoWrite task status management test successful")

def test_task_agent_general():
    """Test Task tool with general-purpose agent"""
    tester = TaskManagementToolsTest()
    
    task_tool = {
        "name": "Task",
        "description": "Launch a new agent to handle complex, multi-step tasks autonomously",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "prompt": {"type": "string"},
                "subagent_type": {"type": "string"}
            },
            "required": ["description", "prompt", "subagent_type"]
        }
    }
    
    message = "Launch a general-purpose agent to research the best Python web frameworks for 2024 and create a comparison report"
    calls = tester.send_request([task_tool], message)
    
    assert len(calls) > 0, "Task general agent tool not called"
    assert calls[0]["name"] == "Task", "Wrong tool called"
    
    # Verify required parameters are present
    tool_input = calls[0].get("input", {})
    assert "description" in tool_input, "description parameter missing"
    assert "prompt" in tool_input, "prompt parameter missing" 
    assert "subagent_type" in tool_input, "subagent_type parameter missing"
    
    print("✅ Task general-purpose agent test successful")

def test_task_agent_statusline():
    """Test Task tool with statusline-setup agent"""
    tester = TaskManagementToolsTest()
    
    task_tool = {
        "name": "Task",
        "description": "Launch a new agent to handle complex, multi-step tasks autonomously",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "prompt": {"type": "string"},
                "subagent_type": {"type": "string"}
            },
            "required": ["description", "prompt", "subagent_type"]
        }
    }
    
    message = "Configure my Claude Code status line settings to show current git branch and file type"
    calls = tester.send_request([task_tool], message)
    
    assert len(calls) > 0, "Task statusline agent tool not called"
    assert calls[0]["name"] == "Task", "Wrong tool called"
    
    print("✅ Task statusline-setup agent test successful")

def test_task_agent_output_style():
    """Test Task tool with output-style-setup agent"""
    tester = TaskManagementToolsTest()
    
    task_tool = {
        "name": "Task",
        "description": "Launch a new agent to handle complex, multi-step tasks autonomously",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "prompt": {"type": "string"},
                "subagent_type": {"type": "string"}
            },
            "required": ["description", "prompt", "subagent_type"]
        }
    }
    
    message = "Create a custom Claude Code output style for my development workflow"
    calls = tester.send_request([task_tool], message)
    
    assert len(calls) > 0, "Task output-style agent tool not called"
    assert calls[0]["name"] == "Task", "Wrong tool called"
    
    print("✅ Task output-style-setup agent test successful")

def test_task_complex_research():
    """Test Task tool for complex research tasks"""
    tester = TaskManagementToolsTest()
    
    task_tool = {
        "name": "Task",
        "description": "Launch a new agent to handle complex, multi-step tasks autonomously",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "prompt": {"type": "string"},
                "subagent_type": {"type": "string"}
            },
            "required": ["description", "prompt", "subagent_type"]
        }
    }
    
    message = "Research and analyze the current state of AI code generation tools, compare their features, and provide recommendations for our development team"
    calls = tester.send_request([task_tool], message)
    
    assert len(calls) > 0, "Task complex research tool not called"
    assert calls[0]["name"] == "Task", "Wrong tool called"
    
    print("✅ Task complex research test successful")

def test_exitplanmode_basic():
    """Test ExitPlanMode tool for presenting implementation plans"""
    tester = TaskManagementToolsTest()
    
    exitplanmode_tool = {
        "name": "ExitPlanMode",
        "description": "Exit plan mode and present plan for user approval",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan": {"type": "string"}
            },
            "required": ["plan"]
        }
    }
    
    message = "I've finished planning the implementation. Present this plan: 1. Setup database schema 2. Create API endpoints 3. Build frontend components 4. Add authentication 5. Write tests"
    calls = tester.send_request([exitplanmode_tool], message)
    
    assert len(calls) > 0, "ExitPlanMode tool not called"
    assert calls[0]["name"] == "ExitPlanMode", "Wrong tool called"
    
    # Verify plan parameter is present
    tool_input = calls[0].get("input", {})
    assert "plan" in tool_input, "plan parameter missing"
    
    print("✅ ExitPlanMode basic test successful")

def test_exitplanmode_detailed_plan():
    """Test ExitPlanMode tool with detailed implementation plan"""
    tester = TaskManagementToolsTest()
    
    exitplanmode_tool = {
        "name": "ExitPlanMode",
        "description": "Exit plan mode and present plan for user approval",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan": {"type": "string"}
            },
            "required": ["plan"]
        }
    }
    
    message = "Present my detailed microservices architecture plan with service boundaries, data flow, deployment strategy, and monitoring approach for user approval"
    calls = tester.send_request([exitplanmode_tool], message)
    
    assert len(calls) > 0, "ExitPlanMode detailed tool not called"
    assert calls[0]["name"] == "ExitPlanMode", "Wrong tool called"
    
    print("✅ ExitPlanMode detailed plan test successful")

def test_task_management_workflow():
    """Test complete task management workflow: TodoWrite -> Task -> ExitPlanMode"""
    tester = TaskManagementToolsTest()
    
    all_tools = [
        {
            "name": "TodoWrite",
            "description": "Create and manage a structured task list",
            "input_schema": {
                "type": "object",
                "properties": {
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
                "required": ["todos"]
            }
        },
        {
            "name": "Task",
            "description": "Launch a new agent for complex tasks",
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "prompt": {"type": "string"},
                    "subagent_type": {"type": "string"}
                },
                "required": ["description", "prompt", "subagent_type"]
            }
        },
        {
            "name": "ExitPlanMode",
            "description": "Present plan for user approval",
            "input_schema": {
                "type": "object",
                "properties": {
                    "plan": {"type": "string"}
                },
                "required": ["plan"]
            }
        }
    ]
    
    message = "I need to plan and implement a complete CI/CD pipeline for our microservices. First create a todo list, then launch an agent to research best practices, and finally present the comprehensive implementation plan for approval."
    calls = tester.send_request(all_tools, message)
    
    assert len(calls) > 0, "No task management tools called in workflow"
    
    # Should call at least one task management tool
    tool_names = [call["name"] for call in calls]
    task_mgmt_tools = {"TodoWrite", "Task", "ExitPlanMode"}
    called_tools = set(tool_names) & task_mgmt_tools
    
    assert len(called_tools) > 0, f"No task management tools called. Called: {tool_names}"
    
    print(f"✅ Task management workflow test successful - Called: {list(called_tools)}")

def test_task_management_tools_comprehensive():
    """Run all task management tools tests"""
    print("🧪 Testing Task Management Tools...")
    
    test_todowrite_basic_planning()
    test_todowrite_complex_project()
    test_todowrite_task_status_management()
    test_task_agent_general()
    test_task_agent_statusline()
    test_task_agent_output_style()
    test_task_complex_research()
    test_exitplanmode_basic()
    test_exitplanmode_detailed_plan()
    test_task_management_workflow()
    
    print("✅ All task management tools tests passed!")

if __name__ == "__main__":
    test_task_management_tools_comprehensive()