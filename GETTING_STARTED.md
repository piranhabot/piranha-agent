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
from piranha import Agent

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
- **46+ Skills**: Built-in skills for various tasks.
- **Rust Core**: Fast, secure, and robust execution.

## Next Steps

- Explore the [User Guide](docs/UI_GUIDE.md).
- Check the [API Reference](docs/reference.md).
- Try the examples in `examples/`.
