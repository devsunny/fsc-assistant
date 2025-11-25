import { MCPClient } from '../src/llm/mcp';

describe('MCP Client', () => {
  let mcp: MCPClient;

  beforeEach(() => {
    mcp = new MCPClient();
  });

  it('should initialize with empty context', () => {
    const context = mcp.getContext();
    expect(context.messages).toHaveLength(0);
    expect(context.temperature).toBe(0.7);
  });

  it('should add messages to context', () => {
    mcp.addMessage('user', 'Hello');
    mcp.addMessage('assistant', 'Hi there!');
    
    const context = mcp.getContext();
    expect(context.messages).toHaveLength(2);
    expect(context.messages[0].role).toBe('user');
    expect(context.messages[1].role).toBe('assistant');
  });

  it('should clear context properly', () => {
    mcp.addMessage('user', 'Hello');
    mcp.clearContext();
    
    const context = mcp.getContext();
    expect(context.messages).toHaveLength(0);
  });

  it('should set parameters correctly', () => {
    mcp.setParameters({
      temperature: 0.9,
      maxTokens: 500
    });
    
    const context = mcp.getContext();
    expect(context.temperature).toBe(0.9);
    expect(context.maxTokens).toBe(500);
  });

  it('should get prompt messages correctly', () => {
    mcp.addMessage('user', 'Hello');
    mcp.addMessage('assistant', 'Hi there!');
    
    const promptMessages = mcp.getPromptMessages();
    expect(promptMessages).toHaveLength(2);
    expect(promptMessages[0].role).toBe('user');
  });
});