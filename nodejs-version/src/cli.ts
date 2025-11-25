#!/usr/bin/env node

import { Command } from 'commander';
import { startShell } from './agents/shell';

const program = new Command();

program
  .name('fsc')
  .description('FSC Assistant - AI-powered development assistant')
  .version('0.1.0')
  .option('-c, --config <path>', 'Path to configuration file')
  .option('--no-history', 'Disable command history');

// Add a command for direct tool execution (for testing purposes)
program
  .command('tool <tool-name>')
  .description('Execute a specific tool directly')
  .option('-p, --params <params>', 'Tool parameters')
  .action((toolName, options) => {
    console.log(`Executing tool: ${toolName}`);
    console.log(`Parameters: ${options.params || 'None'}`);
    
    // In a real implementation, this would execute the specific tool
    console.log('This demonstrates how tools can be invoked directly.');
  });

// Handle default case - start interactive shell when no command is given
program.action((options) => {
  // Start interactive shell by default
  startShell(options);
});

program.parse();