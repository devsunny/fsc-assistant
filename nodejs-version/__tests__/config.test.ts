import { ConfigManager } from '../src/config/manager';

describe('ConfigManager', () => {
  it('should load default config when no file is provided', () => {
    const config = ConfigManager.loadConfig();
    expect(config.llm.provider).toBe('openai');
    expect(config.llm.model).toBe('gpt-4');
  });
});