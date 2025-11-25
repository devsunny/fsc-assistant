#!/bin/bash

# Deployment script for FSC Assistant Node.js version

set -e

echo "Starting FSC Assistant deployment..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
  echo "Error: package.json not found. Are you in the correct directory?"
  exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
npm run clean

# Install dependencies
echo "Installing dependencies..."
npm install

# Run tests to ensure everything works
echo "Running tests..."
npm test

# Build the project
echo "Building project..."
npm run build

# Create distribution directory structure
echo "Creating distribution files..."
mkdir -p dist/

# Copy necessary files to dist
cp README.md dist/
cp CONFIGURATION.md dist/
cp LICENSE dist/
cp package.json dist/

echo "Deployment completed successfully!"
echo ""
echo "To publish to npm:"
echo "  cd dist/"
echo "  npm publish"
echo ""
echo "To test locally:"
echo "  cd dist/"
echo "  npm link"
echo "  fsc --help"

exit 0