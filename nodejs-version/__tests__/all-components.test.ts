/**
 * Comprehensive test suite for all FSC Assistant components
 */

import { ConfigManager } from '../src/config/manager';
import { LLMClient } from '../src/llm/agent_client';
import { ChatHistory } from '../src/agents/history';
import { getTools, findTool } from '../src/agents/tools';
import { MCPClient } from '../src/llm/mcp';
import { analyzeText, extractKeywords } from '../src/agents/tools/document_analysis';

describe('FSC Assistant - Complete Component Tests', () => {
  
  describe('Configuration Management', () => {
    it('should load default configuration when no file exists', () => {
      const config = ConfigManager.loadConfig();
      expect(config.llm.provider).toBe('openai');
      expect(config.llm.model).toBe('gpt-4');
    });
    
    // Note: Actual TOML parsing tests would require a real config file
  });

  describe('Chat History', () => {
    let history: ChatHistory;
    
    beforeEach(() => {
      history = new ChatHistory();
    });
    
    it('should add and retrieve messages', () => {
      history.addMessage('user', 'Hello');
      history.addMessage('assistant', 'Hi there!');
      
      const messages = history.getMessages();
      expect(messages).toHaveLength(2);
      expect(messages[0].role).toBe('user');
      expect(messages[1].role).toBe('assistant');
    });
    
    it('should clear history properly', () => {
      history.addMessage('user', 'Hello');
      history.clear();
      
      const messages = history.getMessages();
      expect(messages).toHaveLength(0);
    });
  });

  describe('Tool Registry', () => {
    it('should have multiple tools registered', () => {
      const tools = getTools();
      expect(tools.length).toBeGreaterThan(0);
    });
    
    it('should find specific tools by name', () => {
      const fileTool = findTool('save_text_file');
      expect(fileTool).toBeDefined();
      
      const searchTool = findTool('google_search');
      expect(searchTool).toBeDefined();
    });
  });

  describe('MCP Client', () => {
    let mcp: MCPClient;
    
    beforeEach(() => {
      mcp = new MCPClient();
    });
    
    it('should initialize with default context', () => {
      const context = mcp.getContext();
      expect(context.messages).toHaveLength(0);
      expect(context.temperature).toBe(0.7);
    });
    
    it('should add messages to context', () => {
      mcp.addMessage('user', 'Hello');
      mcp.addMessage('assistant', 'Hi there!');
      
      const promptMessages = mcp.getPromptMessages();
      expect(promptMessages).toHaveLength(2);
    });
  });

  describe('Document Analysis', () => {
    it('should analyze empty text correctly', () => {
      const result = analyzeText('');
      expect(result.wordCount).toBe(0);
      expect(result.characterCount).toBe(0);
    });
    
    it('should analyze simple text correctly', () => {
      const text = 'Hello world. This is a test.';
      const result = analyzeText(text);
      
      expect(result.wordCount).toBe(6);
      expect(result.characterCount).toBe(27);
      expect(result.sentenceCount).toBe(2);
    });
    
    it('should extract keywords correctly', () => {
      const text = 'The quick brown fox jumps over the lazy dog. The fox is quick and brown.';
      const keywords = extractKeywords(text, 3);
      
      expect(keywords).toHaveLength(3);
    });
  });

  describe('Integration Tests', () => {
    it('should demonstrate complete system functionality', () => {
      // Verify all major components can be imported and instantiated
      const tools = getTools();
      const history = new ChatHistory();
      const mcp = new MCPClient();
      
      expect(tools).toHaveLengthGreaterThan(0);
      expect(history).toBeDefined();
      expect(mcp).toBeDefined();
    });
  });
});