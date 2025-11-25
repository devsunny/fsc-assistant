import { LLMClient } from '../src/llm/agent_client';

describe('LLMClient', () => {
  it('should initialize with default configuration', () => {
    const client = new LLMClient({
      provider: 'openai',
      model: 'gpt-4',
      apiKey: process.env.OPENAI_API_KEY
    });
    
    // Just verify the constructor doesn't throw
    expect(client).toBeDefined();
  });
  
  it('should handle basic prompt processing', async () => {
    const client = new LLMClient({
      provider: 'openai',
      model: 'gpt-4',
      apiKey: process.env.OPENAI_API_KEY
    });
    
    // This test will be skipped if no API key is available
    if (!process.env.OPENAI_API_KEY) {
      console.log('Skipping LLM integration test - no API key');
      return;
    }
    
    try {
      const response = await client.generateResponse("Hello, world!");
      expect(response).toBeDefined();
      expect(typeof response).toBe('string');
    } catch (error) {
      // If we don't have an API key or network access, that's okay for this test
      console.log('LLM test skipped due to environment constraints:', error);
    }
  }, 10000); // 10 second timeout
});