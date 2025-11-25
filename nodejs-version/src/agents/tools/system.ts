import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

export const executeCommand = async (command: string): Promise<{ stdout: string; stderr: string }> => {
  try {
    const result = await execPromise(command);
    return result;
  } catch (error) {
    throw new Error(`Command execution failed: ${error}`);
  }
};

export const getSystemInfo = (): { platform: string; arch: string; hostname: string } => {
  return {
    platform: process.platform,
    arch: process.arch,
    hostname: require('os').hostname()
  };
};

export const getCurrentDirectory = (): string => {
  return process.cwd();
};