# Piranha Agent VS Code Extension

AI Agent development with Piranha - Build, debug, and deploy autonomous agents directly from VS Code.

## Features

- 🤖 **Agent Management** - Create and manage AI agents
- 📋 **Task Creation** - Define and run tasks for your agents
- 🛠️ **Skills Browser** - Browse 46+ Claude Skills
- 💬 **Agent Chat** - Chat with your AI agents
- 🔍 **Time-Travel Debugger** - Debug agent decisions step-by-step
- ▶️ **Quick Run** - Execute agents and tasks with one click

## Getting Started

1. **Install Piranha Agent**:
   ```bash
   pip install piranha-agent
   ```

2. **Start Ollama** (for local LLM):
   ```bash
   ollama serve
   ```

3. **Open Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`)

4. **Search for Piranha commands**:
   - `Piranha: Create New Agent`
   - `Piranha: Create Task`
   - `Piranha: Open Time-Travel Debugger`
   - `Piranha: Chat with Agent`
   - `Piranha: Show Available Skills`

## Usage

### Create an Agent

1. Click the **+** icon in the Agents view
2. Enter agent name
3. Select LLM model (Ollama, Anthropic, OpenAI)
4. Agent configuration file is created automatically

### Run a Task

1. Open a Python file with Piranha code
2. Click the **Play** icon in the editor title
3. Task executes in the integrated terminal

### Chat with Agent

1. Run `Piranha: Chat with Agent` command
2. Chat panel opens in sidebar
3. Type your message and get AI responses

### Debug Agents

1. Run `Piranha: Open Time-Travel Debugger`
2. Debugger opens in browser at `http://localhost:7860`
3. Step through agent decisions and state changes

## Commands

| Command | Description |
|---------|-------------|
| `Piranha: Create New Agent` | Create a new AI agent configuration |
| `Piranha: Run Agent` | Execute the current agent |
| `Piranha: Debug Agent` | Open debugger for the agent |
| `Piranha: Create Task` | Create a new task for an agent |
| `Piranha: Run Task` | Execute the current task |
| `Piranha: Open Time-Travel Debugger` | Launch the time-travel debugger |
| `Piranha: Show Available Skills` | Browse 46+ Claude Skills |
| `Piranha: Chat with Agent` | Open chat panel to talk with agent |

## Requirements

- Python 3.10+
- Piranha Agent (`pip install piranha-agent`)
- Ollama (optional, for local LLM)

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `piranha.apiBase` | `http://localhost:8000` | Piranha API base URL |
| `piranha.defaultModel` | `ollama/llama3:latest` | Default LLM model |
| `piranha.debuggerPort` | `7860` | Time-travel debugger port |

## Known Issues

- Debugger requires `piranha debug` to be running
- Chat panel requires agent to be initialized

## Release Notes

### 0.3.0
- Initial release of Piranha Agent VS Code extension
- Agent and task management
- Chat panel integration
- Time-travel debugger integration
- Skills browser

## Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/piranha-agent/piranha-agent).

## License

MIT OR Apache-2.0

---

**Enjoy building AI agents with Piranha!** 🐟
