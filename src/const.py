"""
Claude Router shared constants
"""

# Claude Code supported tools
SUPPORTED_CLAUDE_TOOLS = {
    'Write', 'Read', 'Edit', 'MultiEdit', 'Bash', 'Glob', 'Grep', 'LS', 
    'TodoWrite', 'Task', 'WebFetch', 'WebSearch', 'NotebookEdit', 'BashOutput', 
    'KillBash', 'ExitPlanMode', 'mcp__ide__getDiagnostics', 'mcp__ide__executeCode'
}

# Default configuration values
DEFAULT_MODEL_NAME = "gpt-oss:20b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 4000

# Default signature secret for HMAC
DEFAULT_SIGNATURE_SECRET = "my-secret-key"