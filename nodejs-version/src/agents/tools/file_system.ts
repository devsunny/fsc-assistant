import fs from 'fs/promises';
import path from 'path';

export const saveTextFile = async (filePath: string, content: string): Promise<string> => {
  try {
    // Ensure directory exists
    const dir = path.dirname(filePath);
    await fs.mkdir(dir, { recursive: true });
    
    // Write file
    await fs.writeFile(filePath, content, 'utf8');
    return filePath;
  } catch (error) {
    throw new Error(`Failed to save text file: ${error}`);
  }
};

export const loadTextFile = async (filePath: string): Promise<string> => {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    return content;
  } catch (error) {
    throw new Error(`Failed to load text file: ${error}`);
  }
};

export const listFiles = async (directoryPath: string): Promise<string[]> => {
  try {
    const files = await fs.readdir(directoryPath);
    return files;
  } catch (error) {
    throw new Error(`Failed to list files: ${error}`);
  }
};

export const fileExists = async (filePath: string): Promise<boolean> => {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
};

export const createDirectory = async (dirPath: string): Promise<string> => {
  try {
    await fs.mkdir(dirPath, { recursive: true });
    return dirPath;
  } catch (error) {
    throw new Error(`Failed to create directory: ${error}`);
  }
};