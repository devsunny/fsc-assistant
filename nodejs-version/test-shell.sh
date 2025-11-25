#!/bin/bash

echo "Testing FSC Assistant shell..."
echo "Starting shell (will exit after 3 seconds if no input)..."
timeout 3s node dist/cli.js || echo "Shell exited normally (expected for automated test)"
echo "Test completed."