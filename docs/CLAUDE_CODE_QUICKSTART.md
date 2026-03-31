# Claude Code Explorer - Quick Reference

## 🚀 Quick Start

```bash
# Install MCP
pip install mcp

# Run example
python examples/12_claude_code_explorer.py
```

---

## 📦 Import

```python
from piranha_agent import Agent
from piranha_agent.claude_code_explorer import (
    ClaudeCodeExplorer,
    create_claude_explorer_skill,
    ExplorerConfig
)
```

---

## 🎯 5 Skills Available

```python
skills = create_claude_explorer_skill()
# Returns: [list_tools, list_commands, get_tool_source, search_source, get_architecture]
```

| Skill | Description |
|-------|-------------|
| `claude_code.list_tools` | List 40+ agent tools |
| `claude_code.list_commands` | List 50+ slash commands |
| `claude_code.get_tool_source` | Get tool source code |
| `claude_code.search_source` | Search with regex |
| `claude_code.get_architecture` | Get architecture docs |

---

## 💻 Usage Patterns

### Pattern 1: Agent with Skills

```python
agent = Agent(
    name="claude-expert",
    skills=create_claude_explorer_skill(),
)

result = agent.run("List all Claude Code tools")
```

### Pattern 2: Direct API

```python
explorer = ClaudeCodeExplorer()

tools = await explorer.list_tools()
source = await explorer.get_tool_source("BashTool")
results = await explorer.search_source(r"class.*Tool")

await explorer.close()
```

### Pattern 3: Context Manager

```python
async with ClaudeCodeExplorer() as explorer:
    tools = await explorer.list_tools()
    # Auto-closes when exiting context
```

---

## 🔧 API Methods

### Discovery

```python
tools = await explorer.list_tools()
# {"tools": [{"name": "...", "description": "...", ...}]}

commands = await explorer.list_commands()
# {"commands": [{"name": "...", "description": "...", ...}]}
```

### Source Access

```python
source = await explorer.get_tool_source("BashTool")
# TypeScript source code string

source = await explorer.get_command_source("/review")
# TypeScript source code string

content = await explorer.read_source_file(
    "tools/BashTool.ts",
    start_line=1,
    end_line=100
)
```

### Search

```python
results = await explorer.search_source(
    pattern=r"class.*Tool",
    file_glob="tools/*.ts",  # Optional
    limit=50  # Optional
)
# {"matches": [{"path": "...", "line": N, "text": "..."}]}

contents = await explorer.list_directory("tools/")
# {"files": [...], "directories": [...]}
```

### Documentation

```python
arch = await explorer.get_architecture()
# {"overview": "...", "tech_stack": {...}, ...}
```

### Convenience

```python
explanation = await explorer.explain_tool("BashTool")
locations = await explorer.find_implementation("permission check")
comparison = await explorer.compare_tools(["BashTool", "FileEditTool"])
```

---

## 🎯 Common Use Cases

### 1. Find Tool Implementation

```python
# Search for tool class
results = await explorer.search_source(
    r"class.*Tool extends",
    limit=10
)

for match in results['matches']:
    print(f"{match['path']}:{match['line']}")
```

### 2. Analyze All Tools

```python
tools = await explorer.list_tools()

for tool in tools['tools'][:5]:
    source = await explorer.get_tool_source(tool['name'])
    lines = source.split('\n')
    print(f"{tool['name']}: {len(lines)} lines")
```

### 3. Learn Architecture

```python
arch = await explorer.get_architecture()

print("Tech Stack:")
for category, tech in arch['tech_stack'].items():
    print(f"  {category}: {tech}")
```

### 4. Find Permission Checks

```python
results = await explorer.search_source(
    r"permission.*check",
    file_glob="hooks/*.ts"
)

for match in results['matches'][:5]:
    print(f"{match['path']}:{match['line']}")
    print(f"  {match['text'][:80]}")
```

---

## ⚙️ Configuration

```python
config = ExplorerConfig(
    src_root="../src",
    mcp_server_command="node",
    mcp_server_args=["/path/to/mcp-server/dist/index.js"],
    timeout_seconds=60,
)

explorer = ClaudeCodeExplorer(config)
```

---

## 🐛 Troubleshooting

### "MCP not installed"
```bash
pip install mcp
```

### "Connection timeout"
```python
config = ExplorerConfig(timeout_seconds=120)
```

### "Tool not found"
Use exact case-sensitive name from `list_tools()`

---

## 📊 Expected Results

| Operation | Result |
|-----------|--------|
| `list_tools()` | ~40 tools |
| `list_commands()` | ~50 commands |
| `get_architecture()` | Full docs |
| `search_source(r"class.*Tool")` | ~40 matches |

---

## 🔒 Security

- ✅ Read-only access
- ✅ Sandboxed via MCP
- ✅ No credentials needed
- ⚠️ Can read all `src/` files

---

## 📚 Documentation

- **Full Guide:** `docs/CLAUDE_CODE_EXPLORER.md`
- **Example:** `examples/12_claude_code_explorer.py`
- **Tests:** `tests/test_claude_code_explorer.py`
- **Integration:** `CLAUDE_CODE_INTEGRATION.md`

---

## 🎓 Next Steps

1. ✅ Run example: `python examples/12_claude_code_explorer.py`
2. ✅ Explore tools: `await explorer.list_tools()`
3. ✅ Get source: `await explorer.get_tool_source("BashTool")`
4. ✅ Search code: `await explorer.search_source(r"def.*permission")`
5. ✅ Learn architecture: `await explorer.get_architecture()`

---

**Version:** 1.0.0 | **Status:** ✅ Ready
