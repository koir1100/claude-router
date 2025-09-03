# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **universal Claude Router proxy server** that connects local Ollama servers with GPT-OSS models to provide Claude Code functionality for **ANY project**. The Python FastAPI application acts as a proxy between Claude Code and local Ollama instances.

### Universal Usage
- 🌍 **Works with any project**: Python, JavaScript, React, Go, Rust, etc.
- 📁 **Adaptive to any folder structure**: Automatically infers project patterns
- 🔧 **Zero configuration**: Just run `./run.sh` and connect Claude Code
- 🎯 **Smart path inference**: Understands context and creates appropriate file structures

### How to Use with Any Project

1. **Start the Claude Router** (one-time setup):
   ```bash
   cd claude-router/
   ./run.sh
   ```

2. **Navigate to YOUR project**:
   ```bash
   cd /path/to/your/awesome-project/
   ```

3. **Open Claude Code in your project**:
   - Claude Code will automatically use `http://localhost:4000` (configured by router)
   - The router adapts to your project structure automatically

4. **Start coding naturally**:
   - "create auth service" → Creates appropriate auth files for your stack
   - "read the README" → Finds and reads your project's README
   - "add a component" → Creates components in the right location for your framework

## Architecture

### Core Components

- **src/main.py**: FastAPI proxy server that handles Anthropic Messages API compatibility
  - Converts Claude message format to Ollama prompts 
  - Streams responses from Ollama back to Claude Code
  - Handles `/v1/messages`, `/health`, and root endpoints
  - Supports tool calling with proper Ollama format conversion

- **src/util.py**: Utility functions for message and tool conversion
  - `convert_claude_tools_to_ollama()`: Converts Claude tool format to Ollama function calling format
  - `convert_messages_to_ollama_format()`: Handles message format conversion
  - `add_tool_instruction()`: Adds system instructions for tool usage
  - `generate_signature()`: Creates HMAC signatures for thinking blocks

- **src/type.py**: Data classes and type definitions
  - Claude API compatible data structures
  - SSE (Server-Sent Events) response formatting
  - Tool calling event types

- **src/const.py**: Configuration constants
  - Supported Claude Code tools list
  - Default URLs, model names, and secrets
  - Currently configured for `gpt-oss:20b` model

- **src/config.yaml**: Runtime configuration file for customization

- **Docker Setup**: Containerized deployment using Python 3.11-slim base
  - Copies `.claude/settings.local.json` configuration into container
  - Exposes port 4000 for proxy communication

- **Claude Code Integration**: Uses `.claude/settings.local.json` to:
  - Set `ANTHROPIC_BASE_URL` to `http://localhost:4000`
  - Enable all tools with `allowedTools: ["*"]`
  - Configure trust and onboarding flags

### Message Flow

1. Claude Code sends requests to localhost:4000 (proxy)
2. Proxy converts Anthropic message format to Ollama prompt format
3. Proxy forwards to local Ollama server at localhost:11434
4. Ollama responses are streamed back through proxy to Claude Code

## Development Commands

### Running the Proxy Server

```bash
# Set permissions and run setup script
chmod +x run.sh
./run.sh
```

This will:
1. Generate `.claude/settings.local.json` configuration
2. Build Docker image as `claude-router`
3. Run container with port mapping 4000:4000

### Direct Python Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly (alternative to Docker)
python main.py
```

### Docker Commands

```bash
# Build image
docker build -t claude-router .

# Run container
docker run -it --rm -p 4000:4000 claude-router
```

## Prerequisites

- Ollama installed and running locally
- GPT-OSS model pulled: `ollama pull gpt-oss:20b`
- Docker installed for containerized deployment

## Configuration

### Environment Variables

- `MODEL_NAME`: Ollama model to use (default: "gpt-oss:20b")
- `OLLAMA_URL`: Ollama API endpoint (default: "http://localhost:11434/api/generate")

### Claude Code Settings

The proxy automatically generates `.claude/settings.local.json` with:
- Proxy server URL configuration
- All tools enabled
- Trust and onboarding settings pre-configured

### Project Structure

```
claude-router/
├── .claude/                    # Claude Code configuration
│   └── settings.local.json     # Auto-generated Claude Code settings
├── src/                        # Source code
│   ├── main.py                # FastAPI proxy server
│   ├── util.py                # Utility functions for conversion
│   ├── type.py                # Data classes and types
│   ├── const.py               # Configuration constants
│   ├── config.yaml            # Runtime configuration
│   └── deco.py                # Decorators and helpers
├── test/                      # Test files
│   ├── test_tools.py          # Tool calling tests
│   ├── test_ollama_tools.py   # Ollama-specific tests
│   ├── test_all_tools.py      # Comprehensive tool tests
│   └── payload.json           # Test payload data
├── run.sh                     # Setup and run script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── CLAUDE.md                  # This documentation
└── README.md                  # Project overview
```

### Test

Every test must be success.
- The test folder is `./test`.
- Run tests with: `python -m pytest test/`

## References

### Official Documentation

#### Ollama API Documentation
- **Ollama API Reference**: https://github.com/ollama/ollama/blob/main/docs/api.md
  - Complete API endpoint documentation including `/api/chat` for tool calling
  - Function calling and streaming response formats
- **Tool Support Blog**: https://ollama.com/blog/tool-support
  - Official announcement of tool calling capabilities
- **Function Calling Improvements**: https://ollama.com/blog/functions-as-tools
  - Python library 0.4 with enhanced function calling support
- **Streaming with Tool Calling**: https://ollama.com/blog/streaming-tool
  - Real-time streaming responses with tool calling
- **OpenAI Compatibility**: https://ollama.com/blog/openai-compatibility
  - OpenAI Chat Completions API compatibility

#### Claude Code Documentation  
- **Claude Streaming Messages**: https://docs.anthropic.com/en/docs/build-with-claude/streaming
  - Official streaming message format for tool use
  - `input_json_delta` and `partial_json` streaming patterns
- **Claude Code Overview**: https://docs.anthropic.com/en/docs/claude-code/overview
  - Official Claude Code documentation and features
- **Claude Code Github**: https://github.com/anthropics/claude-code
  - Official Claude Code Github Repository

### Technical Articles
- **Ollama API Tutorial**: https://geshan.com.np/blog/2025/02/ollama-api/
  - Comprehensive guide to Ollama API endpoints including function calling
- **Ollama Chat Parameters**: https://medium.com/@laurentkubaski/ollama-chat-endpoint-parameters-21a7ac1252e5
  - Detailed explanation of chat endpoint parameters
- **Claude API Integration Guide**: https://collabnix.com/claude-api-integration-guide-2025-complete-developer-tutorial-with-code-examples/
  - Complete developer tutorial for Claude API integration

### Key Findings
- **Correct Endpoint**: Use `/api/chat` for tool calling, not `/api/generate`
- **Model Support**: `gpt-oss:20b` supports tools, thinking, and completion capabilities
- **Streaming Format**: Tool calls come in final message with `done: true`
- **Message Format**: Claude expects `input_json_delta` with `partial_json` for streaming tool arguments

### Tool Calling Implementation

The proxy successfully converts Claude Code tools to Ollama format:

#### Claude Tool Format (Input)
```json
{
  "name": "Write", 
  "description": "Writes a file to the local filesystem",
  "input_schema": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string"},
      "content": {"type": "string"}
    }
  }
}
```

#### Ollama Tool Format (Output)
```json
{
  "type": "function",
  "function": {
    "name": "Write",
    "description": "Writes a file to the local filesystem", 
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {"type": "string"},
        "content": {"type": "string"}
      }
    }
  }
}
```

#### Supported Tools
All Claude Code tools are supported including:
- Write, Read, Edit, MultiEdit
- Bash, Glob, Grep
- TodoWrite, Task, WebFetch, WebSearch
- NotebookEdit, BashOutput, KillBash
- ExitPlanMode, mcp__ide__* tools

### Current Status
✅ **Tool calling working**: `gpt-oss:20b` successfully generates tool calls  
✅ **Format conversion**: Claude → Ollama tool format conversion implemented  
✅ **Streaming support**: SSE streaming with thinking and tool call support  
⚠️  **Testing needed**: Comprehensive testing of all tool types required