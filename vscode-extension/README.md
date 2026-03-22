# Piranha Agent VS Code Extension

Develop, debug, and monitor autonomous Piranha agents directly from your IDE.

## Features

### 1. 👻 Ghost Text (Inline Completions)
Boost your productivity with context-aware SDK suggestions. Type `agent.` or `task.` in any Python file to see Piranha-specific methods like `run()`, `add_skill()`, and `export_trace()` as inline ghost text.

### 2. 💬 Integrated Agent Chat
Communicate with your local Piranha agents through a built-in chat interface.
- **Server Detection**: Automatically detects if the Piranha monitor is running on `localhost:8080`.
- **Local Context**: The agent has access to your workspace context for better assistance.

### 3. 🛡️ HITL (Human-in-the-Loop) Panel
Found in the Piranha Activity Bar, the **Approvals** view displays actions that require your consent.
- **Security First**: Review and approve file writes or network requests before the agent executes them.
- **Full Control**: Never let an autonomous agent make critical changes without your oversight.

### 4. 📊 Multi-View Monitoring
Monitor your entire agent ecosystem from the sidebar:
- **Agents**: Real-time status and token/cost tracking.
- **Tasks**: Progress of current and historical tasks.
- **Skills**: List of installed capabilities.

## Getting Started

1. **Install Dependencies**:
   ```bash
   cd vscode-extension
   npm install
   ```

2. **Compile**:
   ```bash
   npm run compile
   ```

3. **Launch**:
   Press `F5` in VS Code to open a new window with the Piranha extension enabled.

4. **Connect**:
   Ensure you have started the Piranha monitor in your terminal:
   ```bash
   piranha monitor
   ```

## Requirements

- **Piranha Agent SDK** installed in your environment.
- **Ollama** or other LLM provider configured.

---

**Built for Supervised Autonomy** 🐟
