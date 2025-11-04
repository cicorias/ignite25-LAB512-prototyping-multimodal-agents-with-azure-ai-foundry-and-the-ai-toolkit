# OpenTelemetry Tracing Setup

This document explains how to use OpenTelemetry tracing with the AI Toolkit for Visual Studio Code to observe your AI agent and MCP server operations.

## Overview

Tracing has been configured for:
- **Main Agent (`cora_agent.py`)**: Uses Agent Framework's built-in `setup_observability()` for automatic instrumentation
- **MCP Server (`customer_sales.py`)**: Uses OpenTelemetry manual instrumentation to trace tool calls and database operations

## Prerequisites

1. **AI Toolkit Extension**: Ensure the AI Toolkit extension is installed in VS Code
2. **OpenTelemetry Collector**: The AI Toolkit includes a built-in OpenTelemetry collector running on `localhost:4317`
3. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Main Agent Tracing

The main agent (`cora_agent.py`) uses the Agent Framework's automatic instrumentation:

```python
from agent_framework.observability import setup_observability

setup_observability(
    otlp_endpoint="http://localhost:4317",  # AI Toolkit gRPC endpoint
    enable_sensitive_data=True  # Enable capturing prompts and completions
)
```

This automatically captures:
- Chat completions and streaming
- Agent operations and workflows
- Tool calls and responses
- Prompts and completions (when `enable_sensitive_data=True`)

### MCP Server Tracing

The MCP server (`customer_sales.py`) uses manual OpenTelemetry instrumentation:

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup is called in main()
setup_tracing()
```

This captures:
- Tool invocations (`get_products_by_name`, `get_current_utc_date`)
- Database query parameters
- Error conditions
- Custom attributes (product names, row counts, user IDs)

## Viewing Traces

### Using AI Toolkit in VS Code

1. **Open AI Toolkit Panel**:
   - Click the AI Toolkit icon in the VS Code activity bar
   - Or use Command Palette: `AI Toolkit: Focus on AI Toolkit View`

2. **Navigate to Tracing View**:
   - In the AI Toolkit panel, find the "Tracing" section
   - Click on "View Traces" or use the command: `AI Toolkit: Open Tracing View`

3. **Run Your Agent**:
   ```bash
   python cora_agent.py
   ```

4. **Explore Traces**:
   - Traces will appear in real-time as the agent executes
   - Click on individual traces to see:
     - Span hierarchy
     - Timing information
     - Attributes (parameters, results)
     - Events and errors

### Trace Structure

A typical trace will show:
```
cora_agent
├── ChatAgent.run_stream
│   ├── AzureAIAgentClient.create_and_run
│   ├── Tool: get_products_by_name
│   │   └── Database query operations
│   └── Tool: get_current_utc_date
└── Response generation
```

### What You Can See

- **Request/Response**: Full prompts and completions (when sensitive data is enabled)
- **Tool Calls**: Which tools were called, with what parameters, and what they returned
- **Timing**: How long each operation took
- **Errors**: Stack traces and error details
- **Custom Attributes**:
  - Product names being searched
  - Query parameters (max_rows)
  - RLS user IDs
  - Result counts

## Troubleshooting

### Traces Not Appearing

1. **Check AI Toolkit is Running**:
   - Ensure the AI Toolkit extension is active
   - The OTLP collector should be running on port 4317

2. **Verify Endpoint**:
   - Both agent and MCP server use `http://localhost:4317`
   - Check firewall rules if needed

3. **Check Console Output**:
   - Look for "✓ OpenTelemetry tracing configured" message
   - Check for connection errors in the terminal

### Missing Spans

- Ensure `setup_observability()` is called **before** creating the agent
- For MCP server, `setup_tracing()` is called in `main()` at startup

### Sensitive Data Not Showing

- Set `enable_sensitive_data=True` in `setup_observability()`
- Note: This will capture prompts and completions in traces

## Best Practices

1. **Performance**: Tracing adds minimal overhead but consider disabling in production
2. **Sensitive Data**: Be careful with `enable_sensitive_data=True` if working with confidential information
3. **Sampling**: For high-volume applications, consider implementing sampling strategies
4. **Retention**: Traces are stored locally; clear old traces periodically

## Additional Resources

- [Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/languages/python/)
- [AI Toolkit Documentation](https://learn.microsoft.com/azure/ai-studio/how-to/develop/vscode-extension)

## Disabling Tracing

To disable tracing:

1. **Main Agent**: Comment out or remove the `setup_observability()` call
2. **MCP Server**: Comment out the `setup_tracing()` call in `main()`

Or set the endpoint to `None`:
```python
setup_observability(otlp_endpoint=None)
```
