#!/bin/bash
# Script to run MCP inspector connected to the HTTP server

cd /workspace

echo "Starting MCP Inspector connected to HTTP server..."
npx @modelcontextprotocol/inspector http://localhost:8000/mcp