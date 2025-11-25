// src/config/manager.ts

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey?: string;
}

export interface Config {
  llm: LLMConfig;
  // Add other configuration options as needed
}

export class ConfigManager {
  static loadConfig(configPath?: string): Config {
    // Default configuration
    const defaultConfig: Config = {
      llm: {
        provider: 'openai',
        model: 'gpt-4'
      }
    };
    
    // If a config path is provided, try to load it
    if (configPath) {
      try {
        // In a real implementation, this would read from file
        console.log(`Loading configuration from ${configPath}`);
        // For now return default config
        return defaultConfig;
      } catch (error) {
        console.warn('Failed to load config file, using defaults:', error);
        return defaultConfig;
      }
    }
    
    // Check for environment variables
    const apiKey = process.env.FSC_OPENAI_API_KEY || 
                   process.env.OPENAI_API_KEY ||
                   process.env.FSC_ANTHROPIC_API_KEY || 
                   process.env.ANTHROPIC_API_KEY;
    
    if (apiKey) {
      defaultConfig.llm.apiKey = apiKey;
    }
    
    return defaultConfig;
  }
  
  static saveConfig(config: Config, configPath?: string): void {
    // In a real implementation, this would write to file
    console.log('Saving configuration to:', configPath || 'default location');
    console.log('Configuration:', config);
  }
}

export default ConfigManager;