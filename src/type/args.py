from dataclasses import dataclass
from typing import List, Optional

# ==================================================================
# Tool Argument Dataclasses (Based on claude_code.txt)
# ==================================================================

@dataclass
class TaskArgs:
    description: str
    prompt: str
    subagent_type: str

@dataclass
class BashArgs:
    command: str
    timeout: Optional[int] = None
    description: Optional[str] = None
    run_in_background: Optional[bool] = None

@dataclass
class GlobArgs:
    pattern: str
    path: Optional[str] = None

@dataclass
class GrepArgs:
    pattern: str
    path: Optional[str] = None
    glob: Optional[str] = None
    output_mode: Optional[str] = None
    B: Optional[int] = None  # -B parameter
    A: Optional[int] = None  # -A parameter  
    C: Optional[int] = None  # -C parameter
    n: Optional[bool] = None  # -n parameter
    i: Optional[bool] = None  # -i parameter
    type: Optional[str] = None
    head_limit: Optional[int] = None
    multiline: Optional[bool] = None

@dataclass
class ExitPlanModeArgs:
    plan: str

@dataclass
class ReadArgs:
    file_path: str
    offset: Optional[int] = None
    limit: Optional[int] = None

@dataclass
class EditArgs:
    file_path: str
    old_string: str
    new_string: str
    replace_all: Optional[bool] = False

@dataclass
class MultiEditOperation:
    old_string: str
    new_string: str
    replace_all: Optional[bool] = False

@dataclass
class MultiEditArgs:
    file_path: str
    edits: List[MultiEditOperation]

@dataclass
class WriteArgs:
    file_path: str
    content: str

@dataclass
class NotebookEditArgs:
    notebook_path: str
    new_source: str
    cell_id: Optional[str] = None
    cell_type: Optional[str] = None
    edit_mode: Optional[str] = None

@dataclass
class WebFetchArgs:
    url: str
    prompt: str

@dataclass
class TodoItem:
    content: str
    status: str  # pending, in_progress, completed
    activeForm: str

@dataclass
class TodoWriteArgs:
    todos: List[TodoItem]

@dataclass
class WebSearchArgs:
    query: str
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None

@dataclass
class BashOutputArgs:
    bash_id: str
    filter: Optional[str] = None

@dataclass
class KillBashArgs:
    shell_id: str

# Mapping from tool name to its argument dataclass
TOOL_ARG_CLASSES = {
    "Task": TaskArgs,
    "Bash": BashArgs,
    "Glob": GlobArgs,
    "Grep": GrepArgs,
    "ExitPlanMode": ExitPlanModeArgs,
    "Read": ReadArgs,
    "Edit": EditArgs,
    "MultiEdit": MultiEditArgs,
    "Write": WriteArgs,
    "NotebookEdit": NotebookEditArgs,
    "WebFetch": WebFetchArgs,
    "TodoWrite": TodoWriteArgs,
    "WebSearch": WebSearchArgs,
    "BashOutput": BashOutputArgs,
    "KillBash": KillBashArgs,
}