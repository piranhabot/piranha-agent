# Claude Code Explorer for Piranha Agent

Explore Claude Code's 512K+ lines of source code directly from your Piranha Agents!

---

## 🎯 Overview

The **Claude Code Explorer** skill enables your Piranha Agents to:

- **Discover** all 40+ Claude Code agent tools
- **Explore** all 50+ Claude Code slash commands  
- **Read** source code for any tool or command
- **Search** the entire codebase with regex patterns
- **Navigate** directories and files
- **Understand** the architecture

---

## 📦 Installation

```bash
# Install MCP SDK (required for Claude Code Explorer)
pip install mcp

# That's it! The explorer is included in piranha-agent v0.4.0+
```

---

## 🚀 Quick Start

### Method 1: Direct Usage

```python
import asyncio
from piranha_agent.claude_code_explorer import ClaudeCodeExplorer

async def explore():
    explorer = ClaudeCodeExplorer()
    
    # List all tools
    tools = await explorer.list_tools()
    print(f"Found {len(tools['tools'])} tools")
    
    # Get BashTool source
    source = await explorer.get_tool_source("BashTool")
    print(source[:500])  # First 500 chars
    
    # Search for permission checks
    results = await explorer.search_source(r"permission.*check")
    print(f"Found {len(results['matches'])} matches")
    
    await explorer.close()

asyncio.run(explore())
```

### Method 2: Via Piranha Agent

```python
from piranha_agent import Agent, Task
from piranha_agent.claude_code_explorer import create_claude_explorer_skill

# Create agent with Claude Code Explorer skills
explorer_skills = create_claude_explorer_skill()

agent = Agent(
    name="code-explorer",
    model="ollama/llama3:latest",
    skills=explorer_skills,
)

# Run exploration task
task = Task(
    description="List all Claude Code tools and explain what BashTool does",
    agent=agent,
)

result = task.run()
print(result)
```

---

## 📚 Available Skills

When you use `create_claude_explorer_skill()`, you get these 5 skills:

| Skill | Description |
|-------|-------------|
| `claude_code.list_tools` | List all 40+ agent tools |
| `claude_code.list_commands` | List all 50+ slash commands |
| `claude_code.get_tool_source` | Get source for a specific tool |
| `claude_code.search_source` | Search source with regex |
| `claude_code.get_architecture` | Get architecture overview |

---

## 🔧 API Reference

### ClaudeCodeExplorer Class

```python
from piranha_agent.claude_code_explorer import ClaudeCodeExplorer, ExplorerConfig

# Custom configuration
config = ExplorerConfig(
    src_root="../src",
    mcp_server_command="node",
    mcp_server_args=["/path/to/mcp-server/dist/index.js"],
    timeout_seconds=60,
)

explorer = ClaudeCodeExplorer(config)
```

### Methods

#### Discovery

```python
# List all tools
tools = await explorer.list_tools()
# Returns: {"tools": [{"name": "...", "description": "...", ...}]}

# List all commands
commands = await explorer.list_commands()
# Returns: {"commands": [{"name": "...", "description": "...", ...}]}
```

#### Source Access

```python
# Get tool source
source = await explorer.get_tool_source("BashTool")
# Returns: TypeScript source code as string

# Get command source
source = await explorer.get_command_source("/review")
# Returns: TypeScript source code as string

# Read specific file
content = await explorer.read_source_file(
    "tools/BashTool.ts",
    start_line=1,
    end_line=100
)
```

#### Search

```python
# Search with regex
results = await explorer.search_source(
    pattern=r"class.*Tool extends",
    file_glob="tools/*.ts",  # Optional
    limit=50  # Optional
)
# Returns: {"matches": [{"path": "...", "line": N, "text": "..."}]}

# List directory
contents = await explorer.list_directory("tools/")
# Returns: {"files": [...], "directories": [...]}
```

#### Documentation

```python
# Get architecture overview
arch = await explorer.get_architecture()
# Returns: {"overview": "...", "tech_stack": {...}, ...}
```

### Convenience Methods

```python
# Explain a tool
explanation = await explorer.explain_tool("BashTool")

# Find implementation
locations = await explorer.find_implementation("permission checking")

# Compare tools
comparison = await explorer.compare_tools(["BashTool", "FileEditTool"])
```

---

## 📖 Examples

### Example 1: Discover All Tools

```python
tools = await explorer.list_tools()

for tool in tools['tools']:
    print(f"{tool['name']}: {tool['description']}")
```

**Output:**
```
BashTool: Execute shell commands
FileEditTool: Edit files with partial updates
GrepTool: Search files with ripgrep
AgentTool: Spawn sub-agents
...
```

### Example 2: Find Permission Checks

```python
results = await explorer.search_source(
    r"permission.*check",
    file_glob="hooks/*.ts",
    limit=20
)

for match in results['matches']:
    print(f"{match['path']}:{match['line']}")
    print(f"  {match['text'][:80]}")
```

### Example 3: Analyze Tool Architecture

```python
# Get all tools
tools = await explorer.list_tools()

# Analyze each tool
for tool in tools['tools'][:5]:  # First 5
    source = await explorer.get_tool_source(tool['name'])
    
    # Count lines, find methods, etc.
    lines = source.split('\n')
    methods = [l for l in lines if 'async ' in l or 'function ' in l]
    
    print(f"{tool['name']}: {len(lines)} lines, {len(methods)} methods")
```

### Example 4: Get Architecture

```python
arch = await explorer.get_architecture()

print("Tech Stack:")
for category, tech in arch['tech_stack'].items():
    print(f"  {category}: {tech}")

print("\nKey Files:")
for file in arch['key_files']:
    print(f"  {file['name']}: {file['lines']} lines")
```

---

## 🎯 Use Cases

### 1. Code Understanding Agent

Create an agent that helps understand Claude Code internals:

```python
agent = Agent(
    name="claude-code-expert",
    model="anthropic/claude-3-5-sonnet",
    skills=create_claude_explorer_skill(),
    system_prompt="You are an expert on Claude Code's internals. Use the explorer tools to find and explain implementations."
)
```

### 2. Port Claude Code Tools

Find and port Claude Code tools to Piranha skills:

```python
explorer = ClaudeCodeExplorer()

# Find all file-related tools
file_tools = await explorer.search_source(
    r"class.*File.*Tool",
    limit=10
)

# Get source for each
for match in file_tools['matches']:
    tool_name = match['text'].split()[1]  # Extract class name
    source = await explorer.get_tool_source(tool_name)
    
    # Save for analysis
    with open(f"analysis/{tool_name}.ts", "w") as f:
        f.write(source)
```

### 3. Learn Architecture Patterns

```python
# Find design patterns
patterns = await explorer.search_source(
    r"ParallelPrefetch|LazyLoading|AgentSwarm",
    limit=20
)

# Get architecture doc
arch = await explorer.get_architecture()

# Analyze together
print(arch['design_patterns'])
```

---

## 🔒 Security Notes

The Claude Code Explorer:

- ✅ **Read-only**: Cannot modify Claude Code source
- ✅ **Sandboxed**: Runs via MCP in isolated process
- ✅ **No credentials**: Doesn't require API keys
- ⚠️ **Source access**: Can read all files in `src/` directory

---

## 🐛 Troubleshooting

### "MCP not installed"

```bash
pip install mcp
```

### "Connection timeout"

The MCP server may take time to start on first run. Increase timeout:

```python
config = ExplorerConfig(timeout_seconds=60)
explorer = ClaudeCodeExplorer(config)
```

### "Tool not found"

Tool names are case-sensitive. Use `list_tools()` to get exact names.

### "No matches found"

Try different regex patterns. Claude Code uses TypeScript, so search for:
- `class.*Tool` - Tool classes
- `function.*command` - Command functions
- `interface.*Options` - Type definitions

---

## 📊 Performance

| Operation | Typical Latency |
|-----------|----------------|
| `list_tools()` | 100-500ms |
| `get_tool_source()` | 50-200ms |
| `search_source()` | 200-1000ms |
| `get_architecture()` | 100-300ms |

---

## 🎓 Advanced: Custom MCP Server

Use a self-hosted MCP server instead of npx:

```python
config = ExplorerConfig(
    mcp_server_command="node",
    mcp_server_args=["/path/to/claude-code/mcp-server/dist/index.js"],
)

explorer = ClaudeCodeExplorer(config)
```

---

## 📚 Related

- [Claude Code Repository](https://github.com/nirholas/claude-code)
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Piranha Agent Skills](skills.md)

---

## 🤝 Contributing

Want to add more exploration features?

1. Add new methods to `ClaudeCodeExplorer`
2. Create new skills in `create_claude_explorer_skill()`
3. Add examples to `examples/12_claude_code_explorer.py`
4. Update this documentation

---

**Version:** 1.0.0  
**Author:** Piranha Agent Team  
**License:** MIT
