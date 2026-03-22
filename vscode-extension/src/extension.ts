// The module 'vscode' contains the VS Code extensibility API
import * as vscode from 'vscode';

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {
	console.log('Piranha Agent extension is now active!');

	// Register commands
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.createAgent', createAgent)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.runAgent', runAgent)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.debugAgent', debugAgent)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.createTask', createTask)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.runTask', runTask)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.openDebugger', openDebugger)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.showSkills', showSkills)
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.chatWithAgent', chatWithAgent)
	);

	// Register webview panel for chat
	context.subscriptions.push(
		vscode.commands.registerCommand('piranha.openChat', () => {
			ChatPanel.createOrShow(context.extensionUri);
		})
	);

	// Register tree providers
	const agentProvider = new AgentProvider();
	vscode.window.registerTreeDataProvider('piranhaAgents', agentProvider);
	
	const taskProvider = new TaskProvider();
	vscode.window.registerTreeDataProvider('piranhaTasks', taskProvider);
	
	const skillProvider = new SkillProvider();
	vscode.window.registerTreeDataProvider('piranhaSkills', skillProvider);

	const hitlProvider = new HITLProvider();
	vscode.window.registerTreeDataProvider('piranhaHITL', hitlProvider);

	// Register Inline Completion Provider
	context.subscriptions.push(
		vscode.languages.registerInlineCompletionItemProvider(
			{ language: 'python' },
			new PiranhaInlineCompletionProvider()
		)
	);

	// Create status bar item
	const statusBarItem = vscode.window.createStatusBarItem(
		vscode.StatusBarAlignment.Right,
		100
	);
	statusBarItem.command = 'piranha.openDebugger';
	statusBarItem.text = '$(robot) Piranha';
	statusBarItem.tooltip = 'Piranha Agent - Click to open debugger';
	statusBarItem.show();
	context.subscriptions.push(statusBarItem);
}

// Command implementations
async function createAgent() {
	const name = await vscode.window.showInputBox({
		prompt: 'Enter agent name',
		placeHolder: 'my-agent'
	});
	
	if (!name) {
		return;
	}

	const model = await vscode.window.showQuickPick([
		'ollama/llama3:latest',
		'anthropic/claude-3-5-sonnet',
		'openai/gpt-4',
		'openai/gpt-3.5-turbo'
	], {
		placeHolder: 'Select LLM model'
	});

	if (!model) {
		return;
	}

	// Create agent configuration file
	const agentCode = `from piranha import Agent

agent = Agent(
    name="${name}",
    model="${model}",
    description="AI agent for task automation"
)
`;

	const doc = await vscode.workspace.openTextDocument({
		content: agentCode,
		language: 'python'
	});
	
	await vscode.window.showTextDocument(doc);
	vscode.window.showInformationMessage(`Agent "${name}" created!`);
}

async function runAgent() {
	const editor = vscode.window.activeTextEditor;
	if (!editor) {
		vscode.window.showErrorMessage('No active editor');
		return;
	}

	// Run the Python file
	vscode.commands.executeCommand(
		'python.execInTerminal',
		undefined,
		editor.document.uri
	);
	
	vscode.window.showInformationMessage('Agent execution started!');
}

async function debugAgent() {
	// Open time-travel debugger
	vscode.env.openExternal(vscode.Uri.parse('http://localhost:7860'));
	vscode.window.showInformationMessage('Opening Time-Travel Debugger...');
}

async function createTask() {
	const description = await vscode.window.showInputBox({
		prompt: 'Enter task description',
		placeHolder: 'What should the agent do?'
	});
	
	if (!description) {
		return;
	}

	const taskCode = `from piranha import Agent, Task

agent = Agent(name="assistant", model="ollama/llama3:latest")

task = Task(
    description="${description}",
    agent=agent
)

result = task.run()
print(result)
`;

	const doc = await vscode.workspace.openTextDocument({
		content: taskCode,
		language: 'python'
	});
	
	await vscode.window.showTextDocument(doc);
	vscode.window.showInformationMessage('Task created!');
}

async function runTask() {
	const editor = vscode.window.activeTextEditor;
	if (!editor) {
		vscode.window.showErrorMessage('No active editor');
		return;
	}

	// Run the Python file
	vscode.commands.executeCommand(
		'python.execInTerminal',
		undefined,
		editor.document.uri
	);
	
	vscode.window.showInformationMessage('Task execution started!');
}

async function openDebugger() {
	// Open time-travel debugger in browser
	vscode.env.openExternal(vscode.Uri.parse('http://localhost:7860'));
}

async function showSkills() {
	const skills = [
		'📄 Document: docx, pdf, pptx, xlsx',
		'💻 Development: frontend-design, mcp-builder, TDD',
		'🔍 Research: deep-research, root-cause-tracing',
		'🎨 Creative: canvas-design, brand-guidelines',
		'✍️ Communication: internal-comms, article-extractor',
		'📊 Data: csv-data-summarizer, postgres',
		'📁 Productivity: file-organizer, git-workflows',
		'🌐 Social: reddit-fetch, youtube-transcript',
		'💼 Business: competitive-ads, domain-brainstormer'
	];

	const selected = await vscode.window.showQuickPick(skills, {
		placeHolder: 'Available Claude Skills (46+ total)'
	});

	if (selected) {
		vscode.window.showInformationMessage(`Skill category: ${selected}`);
	}
}

async function chatWithAgent() {
	ChatPanel.createOrShow(vscode.Uri.file(__dirname));
}

// Tree Data Providers
class AgentProvider implements vscode.TreeDataProvider<AgentItem> {
	getTreeItem(element: AgentItem): vscode.TreeItem {
		return element;
	}

	getChildren(element?: AgentItem): Thenable<AgentItem[]> {
		if (element) {
			return Promise.resolve([]);
		}
		return Promise.resolve([
			new AgentItem('Local Agent', 'ollama/llama3:latest', vscode.TreeItemCollapsibleState.None),
			new AgentItem('Cloud Agent', 'anthropic/claude-3-5-sonnet', vscode.TreeItemCollapsibleState.None)
		]);
	}
}

class TaskProvider implements vscode.TreeDataProvider<TaskItem> {
	getTreeItem(element: TaskItem): vscode.TreeItem {
		return element;
	}

	getChildren(element?: TaskItem): Thenable<TaskItem[]> {
		if (element) {
			return Promise.resolve([]);
		}
		return Promise.resolve([
			new TaskItem('Pending Task', 'pending', vscode.TreeItemCollapsibleState.None),
			new TaskItem('Completed Task', 'completed', vscode.TreeItemCollapsibleState.None)
		]);
	}
}

class SkillProvider implements vscode.TreeDataProvider<SkillItem> {
	getTreeItem(element: SkillItem): vscode.TreeItem {
		return element;
	}

	getChildren(element?: SkillItem): Thenable<SkillItem[]> {
		if (element) {
			return Promise.resolve([]);
		}
		return Promise.resolve([
			new SkillItem('📄 Document Skills', vscode.TreeItemCollapsibleState.None),
			new SkillItem('💻 Development Skills', vscode.TreeItemCollapsibleState.None),
			new SkillItem('🔍 Research Skills', vscode.TreeItemCollapsibleState.None),
			new SkillItem('🎨 Creative Skills', vscode.TreeItemCollapsibleState.None)
		]);
	}
}

// Tree Items
class AgentItem extends vscode.TreeItem {
	constructor(
		public readonly label: string,
		public model: string,
		public readonly collapsibleState: vscode.TreeItemCollapsibleState
	) {
		super(label, collapsibleState);
		this.tooltip = `Model: ${model}`;
		this.description = model;
		this.iconPath = new vscode.ThemeIcon('robot');
	}
}

class TaskItem extends vscode.TreeItem {
	constructor(
		public readonly label: string,
		public status: string,
		public readonly collapsibleState: vscode.TreeItemCollapsibleState
	) {
		super(label, collapsibleState);
		this.tooltip = `Status: ${status}`;
		this.description = status;
		this.iconPath = new vscode.ThemeIcon(
			status === 'completed' ? 'check' : 'circle-outline'
		);
	}
}

class SkillItem extends vscode.TreeItem {
	constructor(
		public readonly label: string,
		public readonly collapsibleState: vscode.TreeItemCollapsibleState
	) {
		super(label, collapsibleState);
		this.iconPath = new vscode.ThemeIcon('symbol-method');
	}
}

// Chat Panel
class ChatPanel {
	public static currentPanel: ChatPanel | undefined;
	public static readonly viewType = 'piranha-chat';

	private readonly _panel: vscode.WebviewPanel;
	private readonly _extensionUri: vscode.Uri;
	private _disposables: vscode.Disposable[] = [];

	public static createOrShow(extensionUri: vscode.Uri) {
		const column = vscode.window.activeTextEditor
			? vscode.window.activeTextEditor.viewColumn
			: undefined;

		if (ChatPanel.currentPanel) {
			ChatPanel.currentPanel._panel.reveal(column);
			return;
		}

		const panel = vscode.window.createWebviewPanel(
			ChatPanel.viewType,
			'Piranha Agent Chat',
			column || vscode.ViewColumn.One,
			{
				enableScripts: true,
				localResourceRoots: [
					vscode.Uri.joinPath(extensionUri, 'media')
				]
			}
		);

		ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
	}

	private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
		this._panel = panel;
		this._extensionUri = extensionUri;

		// Set HTML content
		this._update();

		// Listen for panel disposal
		this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
	}

	public dispose() {
		ChatPanel.currentPanel = undefined;
		this._panel.dispose();
		while (this._disposables.length) {
			const disposable = this._disposables.pop();
			if (disposable) {
				disposable.dispose();
			}
		}
	}

	private _update() {
		this._panel.title = 'Chat with Piranha Agent';
		this._panel.webview.html = this._getHtmlForWebview();
	}

	private _getHtmlForWebview() {
		return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Piranha Agent Chat</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 100px);
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            border: 1px solid var(--vscode-widget-border);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .message {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 8px;
            word-wrap: break-word;
        }
        .user-message {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            align-self: flex-end;
            margin-left: 20%;
        }
        .agent-message {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            margin-right: 20%;
        }
        .input-container {
            display: flex;
            gap: 8px;
        }
        input {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid var(--vscode-widget-border);
            border-radius: 4px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
        }
        button {
            padding: 8px 16px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            opacity: 0.9;
        }
        .status-bar {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <h2>💬 Chat with Piranha Agent</h2>
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message agent-message">
                <strong>Agent:</strong> Hello! I'm your Piranha AI assistant. How can I help you today?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Ask me to code, search, or automate..." />
            <button id="sendBtn">Send</button>
        </div>
        <div class="status-bar" id="status">Server: Checking connection...</div>
    </div>
    <script>
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const statusDiv = document.getElementById('status');

        async function checkServer() {
            try {
                const response = await fetch('http://localhost:8080/api/health');
                if (response.ok) {
                    statusDiv.innerHTML = '🟢 Server: Online (localhost:8080)';
                    statusDiv.style.color = 'var(--vscode-testing-iconPassedColor)';
                } else {
                    throw new Error();
                }
            } catch (e) {
                statusDiv.innerHTML = '🔴 Server: Offline (Start piranha monitor first)';
                statusDiv.style.color = 'var(--vscode-testing-iconFailedColor)';
            }
        }
        checkServer();

        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        sendBtn.addEventListener('click', sendMessage);

        function addMessage(sender, text, type) {
            const msg = document.createElement('div');
            msg.className = 'message ' + type + '-message';
            msg.innerHTML = '<strong>' + sender + ':</strong> ' + text;
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage('You', message, 'user');
            userInput.value = '';

            const loadingMsg = document.createElement('div');
            loadingMsg.className = 'message agent-message';
            loadingMsg.id = 'loading';
            loadingMsg.innerHTML = '<em>Agent is thinking...</em>';
            messagesDiv.appendChild(loadingMsg);

            try {
                const response = await fetch('http://localhost:8080/api/agents/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                }).catch(() => null);

                const loading = document.getElementById('loading');
                if (loading) loading.remove();

                if (response && response.ok) {
                    const data = await response.json();
                    addMessage('Agent', data.response, 'agent');
                } else {
                    setTimeout(() => {
                        addMessage('Agent', 'I detected your server is offline, but I can still help with local context! To enable full autonomy, run "piranha monitor" in your terminal.', 'agent');
                    }, 800);
                }
            } catch (e) {
                const loading = document.getElementById('loading');
                if (loading) loading.remove();
                addMessage('System', 'Connection error. Please ensure Piranha monitor is running.', 'agent');
            }
        }
    </script>
</body>
</html>`;
	}
}

// Inline Completion Provider for "Ghost Text"
class PiranhaInlineCompletionProvider implements vscode.InlineCompletionItemProvider {
	async provideInlineCompletionItems(
		document: vscode.TextDocument,
		position: vscode.Position,
		context: vscode.InlineCompletionContext,
		token: vscode.CancellationToken
	): Promise<vscode.InlineCompletionList | vscode.InlineCompletionItem[]> {
		
		const linePrefix = document.lineAt(position).text.substr(0, position.character);
		
		// Only trigger after "agent." or "task." or at start of line
		if (!linePrefix.endsWith('agent.') && !linePrefix.endsWith('task.') && linePrefix.trim() !== '') {
			return [];
		}

		// Simple ghost text suggestions for Piranha SDK
		const items: vscode.InlineCompletionItem[] = [];
		
		if (linePrefix.endsWith('agent.')) {
			items.push(new vscode.InlineCompletionItem('run("Task description")'));
			items.push(new vscode.InlineCompletionItem('add_skill(my_skill)'));
			items.push(new vscode.InlineCompletionItem('export_trace()'));
		} else if (linePrefix.endsWith('task.')) {
			items.push(new vscode.InlineCompletionItem('run()'));
			items.push(new vscode.InlineCompletionItem('add_subtask("Description")'));
		}

		return items;
	}
}

// HITL Approval Provider
class HITLProvider implements vscode.TreeDataProvider<ApprovalItem> {
	private _onDidChangeTreeData: vscode.EventEmitter<ApprovalItem | undefined | void> = new vscode.EventEmitter<ApprovalItem | undefined | void>();
	readonly onDidChangeTreeData: vscode.Event<ApprovalItem | undefined | void> = this._onDidChangeTreeData.event;

	getTreeItem(element: ApprovalItem): vscode.TreeItem {
		return element;
	}

	getChildren(element?: ApprovalItem): Thenable<ApprovalItem[]> {
		if (element) {
			return Promise.resolve([]);
		}
		return Promise.resolve([
			new ApprovalItem('Approve: File Write', 'agent-1', 'write to config.yaml', vscode.TreeItemCollapsibleState.None),
			new ApprovalItem('Approve: Network Request', 'agent-2', 'GET https://api.github.com', vscode.TreeItemCollapsibleState.None)
		]);
	}
}

class ApprovalItem extends vscode.TreeItem {
	constructor(
		public readonly label: string,
		public agentId: string,
		public action: string,
		public readonly collapsibleState: vscode.TreeItemCollapsibleState
	) {
		super(label, collapsibleState);
		this.tooltip = `Agent ${agentId} wants to: ${action}`;
		this.description = agentId;
		this.contextValue = 'approval';
		this.iconPath = new vscode.ThemeIcon('shield');
	}
}

// This method is called when your extension is deactivated
export function deactivate() {}
