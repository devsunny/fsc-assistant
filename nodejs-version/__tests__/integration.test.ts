import { getTools } from '../src/agents/tools';

describe('Integration Tests', () => {
  it('should demonstrate tool registry functionality', () => {
    const tools = getTools();
    
    // Verify we have various categories of tools
    const fileTools = tools.filter(t => t.name.includes('file'));
    const systemTools = tools.filter(t => t.name.includes('system') || t.name.includes('execute'));
    const webTools = tools.filter(t => t.name.includes('web') || t.name.includes('fetch'));
    
    expect(fileTools.length).toBeGreaterThan(0);
    expect(systemTools.length).toBeGreaterThan(0);
    expect(webTools.length).toBeGreaterThan(0);
    
    console.log(`Integration test - File tools: ${fileTools.length}, System tools: ${systemTools.length}, Web tools: ${webTools.length}`);
  });
});