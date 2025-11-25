// src/agents/tools/system_commands.ts

import { exec } from 'child_process';
import { promisify } from 'util';

const executeCommand = async (command: string): Promise<{ stdout: string; stderr: string }> => {
  const execPromise = promisify(exec);
  
  try {
    const result = await execPromise(command);
    return {
      stdout: result.stdout,
      stderr: result.stderr
    };
  } catch (error) {
    // If command fails, still return the error in stderr
    if (error instanceof Error) {
      return {
        stdout: '',
        stderr: error.message
      };
    }
    throw error;
  }
};

export { executeCommand };