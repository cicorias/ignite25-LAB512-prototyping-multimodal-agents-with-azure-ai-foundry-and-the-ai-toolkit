# OpenTelemetry Tracing Guide

This guide explains how to enable and use OpenTelemetry tracing for the MCP servers in this workspace.

## Overview

Tracing has been added to the following services:
- **Customer Sales MCP Server** (`customer_sales/customer_sales.py`)
- **Sales Analysis MCP Server** (`sales_analysis/sales_analysis.py`)

Both services use OpenTelemetry with automatic instrumentation for:
- FastAPI HTTP endpoints
- AsyncPG database queries

## Prerequisites

### 1. Install Dependencies

Make sure all required tracing packages are installed:

```bash
cd /workspace/src/python
pip install -r requirements.txt
```

The following OpenTelemetry packages are included:
- `opentelemetry-api` - Core API
- `opentelemetry-sdk` - SDK implementation
- `opentelemetry-exporter-otlp` - OTLP exporter for sending traces
- `opentelemetry-instrumentation-fastapi` - Automatic FastAPI instrumentation
- `opentelemetry-instrumentation-asyncpg` - Automatic AsyncPG instrumentation

### 2. Run an OpenTelemetry Collector

You need an OTLP-compatible backend to receive traces. The easiest option is to run a local collector:

#### Option A: Using Docker (Jaeger All-in-One)

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Then access the Jaeger UI at: http://localhost:16686

#### Option B: Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
```

Start it with:
```bash
docker-compose up -d
```

#### Option C: Azure Monitor / Application Insights

To export traces to Azure Monitor, modify the `setup_tracing()` function to use the Azure Monitor exporter:

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# Replace OTLPSpanExporter with:
azure_exporter = AzureMonitorTraceExporter(
    connection_string="YOUR_APPLICATIONINSIGHTS_CONNECTION_STRING"
)
trace_provider.add_span_processor(BatchSpanProcessor(azure_exporter))
```

## Enabling Tracing

Tracing is **disabled by default**. To enable it, add the `--enable-tracing` flag when starting the server:

### Customer Sales Server

```bash
cd /workspace/src/python/mcp_server/customer_sales
python customer_sales.py --enable-tracing
```

### Sales Analysis Server

```bash
cd /workspace/src/python/mcp_server/sales_analysis
python sales_analysis.py --enable-tracing
```

### Running with other options

You can combine tracing with other flags:

```bash
# HTTP mode with tracing
python customer_sales.py --enable-tracing

# STDIO mode with tracing and RLS user
python customer_sales.py --stdio --RLS_USER_ID "123e4567-e89b-12d3-a456-426614174000" --enable-tracing
```

## Viewing Traces

### Using Jaeger UI

1. Open http://localhost:16686 in your browser
2. Select the service from the dropdown:
   - `mcp-zava-sales-customer`
   - `mcp-zava-sales-analysis`
3. Click "Find Traces" to see all traces
4. Click on a trace to see detailed span information

### Understanding Trace Data

Each trace shows:
- **HTTP requests** - Incoming requests to FastAPI endpoints
- **Database queries** - AsyncPG database operations
- **Timing information** - Duration of each operation
- **Request context** - Headers, parameters, and other metadata

## Configuration

### Changing the OTLP Endpoint

By default, traces are sent to `http://localhost:4317`. To use a different endpoint, modify the `setup_tracing()` function in the service files:

```python
otlp_exporter = OTLPSpanExporter(
    endpoint="http://your-collector:4317",
    insecure=True
)
```

### Service Names

Each service has a unique name for identification:
- Customer Sales: `mcp-zava-sales-customer`
- Sales Analysis: `mcp-zava-sales-analysis`

These can be modified in the `setup_tracing()` function.

## Troubleshooting

### Traces not appearing

1. **Check if the collector is running:**
   ```bash
   docker ps | grep jaeger
   ```

2. **Verify the endpoint is accessible:**
   ```bash
   curl http://localhost:4317
   ```

3. **Check server logs** for tracing initialization message:
   ```
   ✅ Tracing initialized for mcp-zava-sales-customer (OTLP endpoint: http://localhost:4317)
   ```

### Connection errors

If you see OTLP connection errors:
- Ensure the collector is running and listening on port 4317
- Check firewall settings
- Verify the endpoint URL is correct

### Performance impact

Tracing adds minimal overhead, but if performance is critical:
- Use sampling (configure in `TracerProvider`)
- Use asynchronous export (already configured via `BatchSpanProcessor`)
- Adjust batch size and timeout settings

## Best Practices

1. **Enable tracing in development** to understand application behavior
2. **Use trace IDs** to correlate logs and traces
3. **Add custom spans** for important business operations if needed
4. **Monitor trace volume** in production to control costs
5. **Use sampling** in high-traffic production environments

## Additional Resources

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Azure Monitor OpenTelemetry](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
