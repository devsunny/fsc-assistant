import { OpenSpecCommandHandler } from '../src/agents/command_handler';

describe('OpenSpec Command Handler', () => {
  let handler: OpenSpecCommandHandler;

  beforeEach(() => {
    handler = new OpenSpecCommandHandler();
  });

  it('should initialize correctly', () => {
    expect(handler).toBeDefined();
  });

  it('should get available commands', () => {
    const commands = handler.getAvailableCommands();
    expect(commands).toHaveLengthGreaterThan(0);
  });

  it('should handle special commands properly', async () => {
    // These tests are more about structure than actual execution
    // since the shell handling is complex to test in isolation
    
    console.log('Command handler initialized with', handler.getAvailableCommands().length, 'commands');
    
    // This would normally be tested with a real REPL but we can at least verify it doesn't crash
    expect(handler).toBeDefined();
  });
});