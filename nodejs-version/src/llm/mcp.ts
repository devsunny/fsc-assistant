/**
 * Model Context Protocol implementation for FSC Assistant
 */

export interface ModelContext {
  messages: Array<{
    role: 'system' | 'user' | 'assistant';
    content: string;
    timestamp?: Date;
  }>;
  
  tools?: string[];
  temperature?: number;
  maxTokens?: number;
  model?: string;
}

export class MCPClient {
  private context: ModelContext = {
    messages: [],
    temperature: 0.7,
    maxTokens: 1000
  };
  
  // Add a message to the context
  addMessage(role: 'system' | 'user' | 'assistant', content: string): void {
    this.context.messages.push({
      role,
      content,
      timestamp: new Date()
    });
  }
  
  // Get current context
  getContext(): ModelContext {
    return { ...this.context };
  }
  
  // Clear the context
  clearContext(): void {
    this.context.messages = [];
  }
  
  // Set model parameters
  setParameters(params: Partial<ModelContext>): void {
    Object.assign(this.context, params);
  }
  
  // Get messages for LLM prompt
  getPromptMessages(): Array<{ role: string; content: string }> {
    return this.context.messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }
  
  // Add tool to context (for tool usage awareness)
  addTool(toolName: string): void {
    if (!this.context.tools) {
      this.context.tools = [];
    }
    
    if (!this.context.tools.includes(toolName)) {
      this.context.tools.push(toolName);
    }
  }
}