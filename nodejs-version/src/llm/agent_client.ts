// src/llm/agent_client.ts

import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey?: string;
}

export class AgentClient {
  private openai: OpenAI | null = null;
  private anthropic: Anthropic | null = null;
  private config: LLMConfig;

  constructor(config: LLMConfig) {
    this.config = config;
    
    // Initialize clients based on provider
    if (config.provider === 'openai' && config.apiKey) {
      this.openai = new OpenAI({
        apiKey: config.apiKey,
      });
    } else if (config.provider === 'anthropic' && config.apiKey) {
      this.anthropic = new Anthropic({
        apiKey: config.apiKey,
      });
    }
  }

  async generateResponse(messages: any[], options?: any): Promise<string> {
    try {
      if (this.config.provider === 'openai' && this.openai) {
        const completion = await this.openai.chat.completions.create({
          model: this.config.model,
          messages,
          ...options
        });
        
        return completion.choices[0].message.content || '';
      } else if (this.config.provider === 'anthropic' && this.anthropic) {
        const completion = await this.anthropic.messages.create({
          model: this.config.model,
          max_tokens: 1024,
          messages
        });
        
        // Handle Anthropic's response structure
        if (completion.content && Array.isArray(completion.content)) {
          return completion.content.map(block => 
            block.type === 'text' ? block.text : ''
          ).join('');
        }
        return '';
      } else {
        throw new Error(`Unsupported provider or missing API key: ${this.config.provider}`);
      }
    } catch (error) {
      console.error('LLM generation error:', error);
      throw error;
    }
  }

  async getAvailableModels(): Promise<string[]> {
    try {
      if (this.config.provider === 'openai' && this.openai) {
        const models = await this.openai.models.list();
        return models.data.map(model => model.id);
      } else if (this.config.provider === 'anthropic' && this.anthropic) {
        // Anthropic doesn't have a list models endpoint in the same way
        return ['claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus'];
      }
      return [];
    } catch (error) {
      console.error('Error getting available models:', error);
      return [];
    }
  }

  static createDefaultClient(): AgentClient {
    const apiKey = process.env.OPENAI_API_KEY || process.env.ANTHROPIC_API_KEY;
    const provider = process.env.LLM_PROVIDER || 'openai';
    const model = process.env.LLM_MODEL || (provider === 'anthropic' ? 'claude-3-haiku' : 'gpt-4');
    
    return new AgentClient({
      provider,
      model,
      apiKey
    });
  }
}

export default AgentClient;