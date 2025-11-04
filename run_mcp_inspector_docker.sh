#!/bin/bash
# Script to run MCP inspector with host binding for Docker access

cd /workspace

echo "Starting MCP Inspector with host binding for Docker access..."

# Set environment variables to bind inspector to all interfaces
export MCP_INSPECTOR_HOST="0.0.0.0"
export MCP_INSPECTOR_PORT="6274"

# Start the inspector
npx @modelcontextprotocol/inspector http://localhost:8000/mcp