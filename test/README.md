# Claude Router Test Suite

Comprehensive test suite for all Claude Code tools through the Claude Router proxy.

## Overview

This test suite validates that the Claude Router correctly handles all 19 supported Claude Code tools:

### File Operations
- **Write**: Creates files on the local filesystem
- **Read**: Reads files from the local filesystem  
- **Edit**: Performs exact string replacements in files
- **MultiEdit**: Makes multiple edits to a single file

### Execution Tools
- **Bash**: Executes bash commands in persistent shell sessions
- **BashOutput**: Retrieves output from background bash shells
- **KillBash**: Terminates running background bash shells

### Search Tools
- **Glob**: Fast file pattern matching
- **Grep**: Powerful content search using ripgrep

### Web Tools
- **WebFetch**: Fetches and processes content from URLs
- **WebSearch**: Searches the web for current information

### Notebook & IDE Tools
- **NotebookEdit**: Edits Jupyter notebook cells
- **mcp__ide__executeCode**: Executes Python code in Jupyter kernel
- **mcp__ide__getDiagnostics**: Gets language diagnostics from VS Code

### Task Management
- **TodoWrite**: Creates and manages structured task lists
- **Task**: Launches specialized agents for complex tasks
- **ExitPlanMode**: Presents implementation plans for approval

## Test Structure

```
test/
├── run_all_tests.py                      # Main test runner
├── pytest.ini                           # Pytest configuration
├── test_claude_tools_comprehensive.py   # All tools in one suite
├── test_file_operations.py             # File operation tools
├── test_execution_tools.py             # Bash execution tools
├── test_search_tools.py                # File and content search
├── test_web_tools.py                   # Web fetching and search
├── test_notebook_and_ide_tools.py      # Notebook and IDE integration
├── test_task_management_tools.py       # Task planning and management
└── README.md                           # This documentation
```

## Running Tests

### Prerequisites

1. **Claude Router running**:
   ```bash
   ./run.sh
   ```

2. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   pip install pytest requests
   ```

### Run All Tests

```bash
# Using the test runner (recommended)
python test/run_all_tests.py

# Using pytest
pytest test/ -v

# Run specific test category
python test/test_file_operations.py
python test/test_web_tools.py
```

### Test Runner Features

The `run_all_tests.py` script provides:

- **Health Check**: Verifies Claude Router is running
- **Comprehensive Coverage**: Tests all 19 Claude Code tools
- **Detailed Reporting**: Success rates, timing, error details
- **JSON Output**: Machine-readable results in `test_results.json`
- **Timeout Handling**: Prevents hanging tests
- **Error Categorization**: PASSED, FAILED, TIMEOUT, ERROR, NOT_FOUND

### Sample Output

```
🚀 Starting Claude Router comprehensive test suite...
🔍 Checking Claude Router health...
✅ Router healthy - Model: gpt-oss:20b

🧪 Running test_file_operations...
✅ test_file_operations PASSED (2.34s)

🧪 Running test_web_tools...
✅ test_web_tools PASSED (8.91s)

📊 CLAUDE ROUTER TEST RESULTS SUMMARY
====================================
🕐 Total Runtime: 45.67s
📁 Total Test Suites: 7
✅ Passed: 7
❌ Failed: 0
📈 Success Rate: 100.0%
```

## Test Categories

### 1. File Operations Tests
- Write/Read file cycles
- String replacement editing
- Multiple file modifications
- Path handling and validation

### 2. Execution Tools Tests  
- Command execution and output capture
- Background process management
- Shell lifecycle management
- Timeout and error handling

### 3. Search Tools Tests
- Pattern matching and globbing
- Content search with regex
- File type filtering
- Case sensitivity and multiline matching

### 4. Web Tools Tests
- URL fetching and processing
- Web search with domain filtering
- Content analysis and summarization
- Error handling for invalid URLs

### 5. Notebook & IDE Tests
- Jupyter notebook cell manipulation
- Code execution in kernel
- Diagnostic information retrieval
- Cell type handling (code/markdown)

### 6. Task Management Tests
- Todo list creation and status management
- Agent launching for complex tasks
- Plan presentation and approval
- Multi-step workflow coordination

## Validation Strategy

Each test verifies:

1. **Tool Call Generation**: Correct tool is called by Ollama
2. **Parameter Validation**: Required parameters are present
3. **Schema Compliance**: Input matches Claude Code schemas
4. **Format Conversion**: Claude → Ollama tool format conversion
5. **Streaming Response**: Proper SSE response handling

## Troubleshooting

### Common Issues

**Router Not Running**:
```
❌ Router connection failed: Connection refused
```
Solution: Run `./run.sh` to start the Claude Router

**Tool Not Called**:
```
AssertionError: Write tool not called
```  
Solution: Check if user message properly triggers the tool

**Timeout Errors**:
```
⏰ test_web_tools TIMEOUT (120.0s)
```
Solution: Check network connectivity for web-based tests

**Model Issues**:
```  
❌ Router health check failed - Status: 500
```
Solution: Verify Ollama is running and `gpt-oss:20b` model is available

### Debug Mode

Add debug output to tests:
```python
print(f"Tool calls: {calls}")
print(f"Tool input: {calls[0].get('input', {})}")
```

### Log Analysis

Check router logs for detailed tool calling:
```bash  
tail -f claude-router.log
```

## Contributing

When adding new tools or tests:

1. **Add tool schema** to the appropriate test file
2. **Create test function** following naming convention `test_toolname_*`
3. **Verify parameters** are correctly passed to Ollama
4. **Update comprehensive suite** with new tool
5. **Document** any special requirements

## Performance Notes

- **Average test time**: 30-60 seconds total
- **Individual tests**: 1-10 seconds each
- **Web tests**: May take longer due to network latency
- **Complex planning**: TodoWrite tests can take 15+ seconds

## Integration with CI/CD

The test suite is designed for automated testing:

```yaml
- name: Test Claude Router
  run: |
    ./run.sh &
    sleep 10
    python test/run_all_tests.py
```

Exit codes:
- `0`: All tests passed
- `1`: Some tests failed
- Check `test/test_results.json` for detailed results