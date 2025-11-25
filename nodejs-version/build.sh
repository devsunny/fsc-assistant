#!/bin/bash

# Build script for FSC Assistant Node.js version

echo "Building FSC Assistant Node.js version..."

# Clean previous builds
npm run clean

# Install dependencies
npm install

# Compile TypeScript to JavaScript
npx tsc

echo "Build completed successfully!"
echo "The built files are in the 'dist' directory."