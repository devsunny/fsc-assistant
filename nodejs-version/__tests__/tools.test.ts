import { getTools, findTool } from '../src/agents/tools';

describe('Tool Registry', () => {
  it('should have multiple tools registered', () => {
    const tools = getTools();
    expect(tools.length).toBeGreaterThan(0);
    console.log(`Found ${tools.length} tools in registry`);
  });

  it('should find specific tools by name', () => {
    const fileTool = findTool('save_text_file');
    expect(fileTool).toBeDefined();
    expect(fileTool?.name).toBe('save_text_file');
    
    const searchTool = findTool('google_search');
    expect(searchTool).toBeDefined();
    expect(searchTool?.name).toBe('google_search');
  });

  it('should handle non-existent tools gracefully', () => {
    const tool = findTool('non_existent_tool');
    expect(tool).toBeUndefined();
  });
});