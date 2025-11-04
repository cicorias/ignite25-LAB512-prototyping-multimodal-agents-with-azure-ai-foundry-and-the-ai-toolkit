#!/bin/bash
# Script to run MCP server in HTTP mode accessible from Docker host

cd /workspace/src/python/mcp_server/customer_sales

echo "Starting MCP server on 0.0.0.0:8000 (accessible from Docker host)..."
# Run the MCP server in HTTP mode (not stdio)
# Server is now configured to bind to 0.0.0.0:8000, making it accessible from Docker host
uv run customer_sales.py --RLS_USER_ID=00000000-0000-0000-0000-000000000000