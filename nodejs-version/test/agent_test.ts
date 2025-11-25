// test/agent_test.ts

import { AgentClient } from '../src/llm/agent_client';

console.log('Testing FSC Assistant components...');

// Test LLM client creation
try {
  const client = AgentClient.createDefaultClient();
  console.log('✓ LLM Client created successfully');
} catch (error) {
  console.error('✗ Failed to create LLM Client:', error);
}

console.log('All tests completed!');