/**
 * Shared type definitions for FSC Assistant Node.js implementation
 */

export interface Tool {
  name: string;
  description: string;
  execute: (...args: any[]) => Promise<any>;
}

export interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'other';
  model: string;
  apiKey?: string;
  baseURL?: string;
}

export interface Config {
  llm: LLMConfig;
  jira?: {
    baseUrl: string;
    token: string;
  };
  github?: {
    token: string;
  };
  google?: {
    apiKey: string;
  };
}