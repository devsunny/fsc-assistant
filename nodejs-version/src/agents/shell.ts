import { ConfigManager } from '../config/manager';
import { AgentClient, LLMConfig } from '../llm/agent_client';

export interface ShellOptions {
  configPath?: string;
  disableHistory?: boolean;
}

// Simple REPL implementation for special commands
export async function startShell(options: ShellOptions = {}) {
  console.log('FSC Assistant Node.js - Interactive Shell');
  console.log('Type "exit", "quit", or "q" to exit the shell.');
  console.log('Use "help" for available commands.');
  console.log('');

  // Load configuration
  try {
    const config = ConfigManager.loadConfig(options.configPath);
    console.log('Configuration loaded successfully.');

    // Initialize LLM client with just the LLM part of config
    const llmConfig: LLMConfig = config.llm;
    const llmClient = new AgentClient(llmConfig);
    console.log('LLM Client initialized successfully.');

    console.log('\nFSC Assistant is ready for use!');
    console.log('Available tools and commands:');
    console.log('- File operations: saveTextFile, loadTextFile, listFiles');
    console.log('- Web operations: fetchWebPage, scrapeTextContent');
    console.log('- Document analysis: analyzeText, extractKeywords');
    console.log('- System commands: executeShellCommand');

    // Start REPL loop
    startRepl(llmClient);

  } catch (error) {
    console.error('Failed to initialize shell:', error);
  }
}

function startRepl(client: AgentClient) {
  const readline = require('readline');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: 'fsc> '
  });

  rl.prompt();

  rl.on('line', (input: string) => {
    const command = input.trim().toLowerCase();

    switch (command) {
      case 'exit':
      case 'quit':
      case 'q':
        console.log('Goodbye!');
        rl.close();
        process.exit(0);
        return;

      case 'help':
        showHelp();
        break;

      default:
        // Process as a regular command
        console.log(`Processing: "${input}"`);
        console.log('In a full implementation, this would be processed by the LLM with appropriate tool usage.');

    }

    rl.prompt();
  }).on('close', () => {
    console.log('\nGoodbye!');
    process.exit(0);
  });
}

function showHelp(): void {
  console.log('FSC Assistant Help:');
  console.log('- help: Show this help message');
  console.log('- exit/quit/q: Exit the shell');
  console.log('- Any other input is processed by LLM with tool usage');
  console.log('');
}

// Export for use in CLI
export default startShell;