#!/usr/bin/env python3
"""
Web Tools Test Suite
Tests: WebFetch, WebSearch
"""
import requests
import json

class WebToolsTest:
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
            timeout=60  # Longer timeout for web requests
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

def test_webfetch_basic():
    """Test WebFetch tool for basic URL fetching"""
    tester = WebToolsTest()
    
    webfetch_tool = {
        "name": "WebFetch",
        "description": "Fetches content from a specified URL and processes it using an AI model",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "prompt": {"type": "string"}
            },
            "required": ["url", "prompt"]
        }
    }
    
    message = "Fetch the homepage of https://example.com and summarize its main content"
    calls = tester.send_request([webfetch_tool], message)
    
    assert len(calls) > 0, "WebFetch tool not called"
    assert calls[0]["name"] == "WebFetch", "Wrong tool called"
    
    # Verify required parameters are present
    tool_input = calls[0].get("input", {})
    assert "url" in tool_input, "URL parameter missing"
    assert "prompt" in tool_input, "Prompt parameter missing"
    
    print("✅ WebFetch basic test successful")

def test_webfetch_with_analysis():
    """Test WebFetch tool with content analysis prompt"""
    tester = WebToolsTest()
    
    webfetch_tool = {
        "name": "WebFetch",
        "description": "Fetches content from a specified URL and processes it using an AI model",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "prompt": {"type": "string"}
            },
            "required": ["url", "prompt"]
        }
    }
    
    message = "Fetch https://httpbin.org/json and extract all key-value pairs from the JSON response"
    calls = tester.send_request([webfetch_tool], message)
    
    assert len(calls) > 0, "WebFetch analysis tool not called"
    assert calls[0]["name"] == "WebFetch", "Wrong tool called"
    
    print("✅ WebFetch with analysis test successful")

def test_webfetch_documentation():
    """Test WebFetch tool for fetching documentation"""
    tester = WebToolsTest()
    
    webfetch_tool = {
        "name": "WebFetch",
        "description": "Fetches content from a specified URL and processes it using an AI model",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "prompt": {"type": "string"}
            },
            "required": ["url", "prompt"]
        }
    }
    
    message = "Fetch the GitHub API documentation from https://docs.github.com/en/rest and summarize the authentication methods"
    calls = tester.send_request([webfetch_tool], message)
    
    assert len(calls) > 0, "WebFetch documentation tool not called"
    assert calls[0]["name"] == "WebFetch", "Wrong tool called"
    
    print("✅ WebFetch documentation test successful")

def test_websearch_basic():
    """Test WebSearch tool for basic web searching"""
    tester = WebToolsTest()
    
    websearch_tool = {
        "name": "WebSearch",
        "description": "Search the web and use the results to inform responses",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "allowed_domains": {"type": "array", "items": {"type": "string"}},
                "blocked_domains": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    }
    
    message = "Search the web for 'Claude AI assistant latest features 2024'"
    calls = tester.send_request([websearch_tool], message)
    
    assert len(calls) > 0, "WebSearch tool not called"
    assert calls[0]["name"] == "WebSearch", "Wrong tool called"
    
    # Verify query parameter is present
    tool_input = calls[0].get("input", {})
    assert "query" in tool_input, "Query parameter missing"
    
    print("✅ WebSearch basic test successful")

def test_websearch_with_domain_filter():
    """Test WebSearch tool with domain filtering"""
    tester = WebToolsTest()
    
    websearch_tool = {
        "name": "WebSearch",
        "description": "Search the web and use the results to inform responses",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "allowed_domains": {"type": "array", "items": {"type": "string"}},
                "blocked_domains": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    }
    
    message = "Search for Python tutorials but only from official documentation sites like python.org and docs.python.org"
    calls = tester.send_request([websearch_tool], message)
    
    assert len(calls) > 0, "WebSearch domain filter tool not called"
    assert calls[0]["name"] == "WebSearch", "Wrong tool called"
    
    print("✅ WebSearch with domain filter test successful")

def test_websearch_current_events():
    """Test WebSearch tool for current events and recent information"""
    tester = WebToolsTest()
    
    websearch_tool = {
        "name": "WebSearch",
        "description": "Search the web and use the results to inform responses",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "allowed_domains": {"type": "array", "items": {"type": "string"}},
                "blocked_domains": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    }
    
    message = "Search for the latest news about artificial intelligence developments in 2024"
    calls = tester.send_request([websearch_tool], message)
    
    assert len(calls) > 0, "WebSearch current events tool not called"
    assert calls[0]["name"] == "WebSearch", "Wrong tool called"
    
    print("✅ WebSearch current events test successful")

def test_websearch_technical_info():
    """Test WebSearch tool for technical information"""
    tester = WebToolsTest()
    
    websearch_tool = {
        "name": "WebSearch",
        "description": "Search the web and use the results to inform responses",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "allowed_domains": {"type": "array", "items": {"type": "string"}},
                "blocked_domains": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    }
    
    message = "Search for best practices for FastAPI application deployment and performance optimization"
    calls = tester.send_request([websearch_tool], message)
    
    assert len(calls) > 0, "WebSearch technical info tool not called"
    assert calls[0]["name"] == "WebSearch", "Wrong tool called"
    
    print("✅ WebSearch technical info test successful")

def test_websearch_with_blocked_domains():
    """Test WebSearch tool with blocked domains"""
    tester = WebToolsTest()
    
    websearch_tool = {
        "name": "WebSearch",
        "description": "Search the web and use the results to inform responses",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "allowed_domains": {"type": "array", "items": {"type": "string"}},
                "blocked_domains": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    }
    
    message = "Search for JavaScript frameworks but exclude results from social media sites like reddit.com and stackoverflow.com"
    calls = tester.send_request([websearch_tool], message)
    
    assert len(calls) > 0, "WebSearch blocked domains tool not called"
    assert calls[0]["name"] == "WebSearch", "Wrong tool called"
    
    print("✅ WebSearch with blocked domains test successful")

def test_web_tools_research_workflow():
    """Test combined web research workflow: WebSearch to find URLs, then WebFetch to get detailed content"""
    tester = WebToolsTest()
    
    all_tools = [
        {
            "name": "WebSearch",
            "description": "Search the web and use the results to inform responses",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "allowed_domains": {"type": "array", "items": {"type": "string"}},
                    "blocked_domains": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["query"]
            }
        },
        {
            "name": "WebFetch",
            "description": "Fetches content from a specified URL and processes it",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "format": "uri"},
                    "prompt": {"type": "string"}
                },
                "required": ["url", "prompt"]
            }
        }
    ]
    
    message = "Research the latest Python web frameworks by searching for recent articles and then fetch detailed information from the most relevant sources"
    calls = tester.send_request(all_tools, message)
    
    assert len(calls) > 0, "No web tools called in research workflow"
    
    # Should call at least one web tool
    tool_names = [call["name"] for call in calls]
    web_tools = {"WebSearch", "WebFetch"}
    called_tools = set(tool_names) & web_tools
    
    assert len(called_tools) > 0, f"No web tools called. Called: {tool_names}"
    
    print(f"✅ Web research workflow test successful - Called: {list(called_tools)}")

def test_web_tools_comprehensive():
    """Run all web tools tests"""
    print("🧪 Testing Web Tools...")
    
    test_webfetch_basic()
    test_webfetch_with_analysis()
    test_webfetch_documentation()
    test_websearch_basic()
    test_websearch_with_domain_filter()
    test_websearch_current_events()
    test_websearch_technical_info()
    test_websearch_with_blocked_domains()
    test_web_tools_research_workflow()
    
    print("✅ All web tools tests passed!")

if __name__ == "__main__":
    test_web_tools_comprehensive()