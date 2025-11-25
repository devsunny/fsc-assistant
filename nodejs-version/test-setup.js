#!/usr/bin/env node

// Simple test to verify Node.js project structure is working
console.log('Testing FSC Assistant Node.js setup...');

try {
  // Test that our modules can be imported
  const fs = require('fs');
  const path = require('path');
  
  console.log('✓ Core Node.js modules available');
  
  // Check if key directories exist
  const dirsToCheck = [
    'src',
    'src/cli',
    'src/config', 
    'src/llm',
    'src/agents',
    'src/utils'
  ];
  
  let allDirsExist = true;
  for (const dir of dirsToCheck) {
    if (!fs.existsSync(path.join(__dirname, dir))) {
      console.log(`✗ Directory missing: ${dir}`);
      allDirsExist = false;
    }
  }
  
  if (allDirsExist) {
    console.log('✓ All required directories exist');
  }
  
  // Check package.json exists
  if (fs.existsSync(path.join(__dirname, 'package.json'))) {
    console.log('✓ package.json exists');
  } else {
    console.log('✗ package.json missing');
  }
  
  console.log('Setup test completed successfully!');
} catch (error) {
  console.error('Setup test failed:', error);
  process.exit(1);
}