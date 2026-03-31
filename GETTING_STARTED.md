# Getting Started with Piranha Agent

Welcome to Piranha Agent! This guide will help you get up and running quickly.

## Configuration

First, set up your environment:

1.  **Environment Variables**: Create a `.env` file in your project root:
    ```bash
    cp .env.example .env
    ```
2.  **API Key**: Add your `ANTHROPIC_API_KEY` to the `.env` file.

## Quick Start (CLI)

Use the CLI to start an interactive session:

```bash
piranha-agent chat
```

## Quick Start (Python)

Create your first agent in Python:

```python
import asyncio
from piranha_agent import Agent

async def main():
    agent = Agent(name="Researcher")
    response = await agent.run("Research the latest trends in AI agents.")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Features

- **Time-Travel Debugging**: Go back in time to inspect state.
- **Wasm Sandbox**: Execute untrusted code safely.
- **51+ Skills**: Built-in skills including Claude Code Explorer.
- **Claude Code Explorer**: Explore 512K+ lines of Claude Code source.
- **Rust Core**: Fast, secure, and robust execution.

## Claude Code Explorer (NEW!)

Explore Claude Code's source code directly from your agents:

```python
from piranha_agent import Agent, create_claude_explorer_skill

agent = Agent(
    name="claude-expert",
    skills=create_claude_explorer_skill(),  # 5 explorer skills
)

result = agent.run("List all Claude Code tools")
print(result)
```

Or use the CLI:
```bash
piranha-agent explore --list-tools
piranha-agent explore --tool BashTool
piranha-agent explore --search "class.*Tool"
```

See [docs/CLAUDE_CODE_EXPLORER.md](docs/CLAUDE_CODE_EXPLORER.md) for full documentation.

## Next Steps

- Explore the [User Guide](docs/UI_GUIDE.md).
- Check the [API Reference](docs/reference.md).
- Try the examples in `examples/`.
