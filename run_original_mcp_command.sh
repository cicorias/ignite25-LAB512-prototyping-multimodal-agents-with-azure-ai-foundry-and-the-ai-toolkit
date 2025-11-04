#!/bin/bash
# Run MCP Inspector with stdio mode - accessible from Docker host

cd /workspace

echo "Starting MCP Inspector with stdio mode..."

# Set environment variables for Docker host access
export MCP_INSPECTOR_HOST=0.0.0.0
export HOST=0.0.0.0

# Run the inspector with your original command but with environment variables
npx @modelcontextprotocol/inspector \
  uv \
  --directory /workspace/src/python/mcp_server/customer_sales \
  run \
  /workspace/src/python/mcp_server/customer_sales/customer_sales.py \
  "--stdio" \
  "--RLS_USER_ID=00000000-0000-0000-0000-000000000000"