# MCP Server Development Mistakes & Solutions

## Date: 2025-10-16
## Project: Scatter Plotter MCP for ChatGPT Integration

### Mistake 1: Using `streamable_http_app()` with uvicorn directly
**Error**: `RuntimeError: Task group is not initialized. Make sure to use run().`

**What I did wrong**:
```python
# WRONG APPROACH
app = mcp.streamable_http_app()
uvicorn.run(app, host=host, port=port)
```

**Why it failed**:
- `streamable_http_app()` returns an ASGI app but doesn't initialize the internal task group
- FastMCP requires `mcp.run()` to properly initialize all internal components
- Direct uvicorn usage bypasses FastMCP's initialization process

**Correct solution**:
```python
# CORRECT APPROACH
mcp.run(transport="sse")  # or other valid transport
```

---

### Mistake 2: Passing `port` and `host` as direct parameters to `mcp.run()`
**Error**: `TypeError: FastMCP.run() got an unexpected keyword argument 'port'`

**What I did wrong**:
```python
# WRONG - FastMCP 2.2.6 doesn't accept these parameters
mcp.run(transport="http", port=port, host=host)
```

**Why it failed**:
- FastMCP 2.2.6 doesn't accept `port` and `host` as direct parameters
- The method signature changed between versions
- Documentation showed newer version API

**Correct solution**:
```python
# Use environment variables instead
os.environ["FASTMCP_SERVER_PORT"] = port
os.environ["FASTMCP_SERVER_HOST"] = host
mcp.run(transport="sse")
```

---

### Mistake 3: Using `transport="http"` with FastMCP 2.2.6
**Error**: `ValueError: Unknown transport: http`

**What I did wrong**:
```python
# WRONG - "http" is not a valid transport in FastMCP 2.2.6
mcp.run(transport="http")
```

**Why it failed**:
- FastMCP 2.2.6 only recognizes: `"stdio"`, `"sse"`, not `"http"`
- "http" or "streamable-http" support was added in later versions
- Need to use SSE for web-based MCP servers in older versions

**Correct solution**:
```python
# Option 1: Use SSE transport (works in 2.2.6)
mcp.run(transport="sse")

# Option 2: Upgrade FastMCP
# requirements.txt: fastmcp>=2.12.0
```

---

### Mistake 4: Using environment variables instead of direct parameters for FastMCP 2.12+
**Error**: Server running on `127.0.0.1:8000` instead of `0.0.0.0:10000`, Render can't detect port

**What I did wrong**:
```python
# WRONG - Environment variables don't work reliably with FastMCP SSE in 2.12+
os.environ["FASTMCP_SERVER_PORT"] = port
os.environ["FASTMCP_SERVER_HOST"] = host
mcp.run(transport="sse")
```

**Why it failed**:
- FastMCP 2.12+ SSE ignores the FASTMCP_SERVER_* environment variables
- Server defaulted to 127.0.0.1:8000
- Render needs server on 0.0.0.0 with the PORT from environment
- Port detection failed, causing deployment to hang

**Correct solution**:
```python
# CORRECT - Pass host and port directly to mcp.run()
port = int(os.environ.get("PORT", 8000))
host = os.environ.get("HOST", "0.0.0.0")
mcp.run(transport="sse", host=host, port=port)
```

---

## Key Learnings

### 1. FastMCP Transport Types (as of 2.12+)
- **`stdio`**: Default, for local command-line tools
- **`sse`**: Server-Sent Events, for web deployment (ChatGPT compatible)
- **`streamable-http`** or **`http`**: Newer HTTP-based transport (requires FastMCP 2.10+)

### 2. ChatGPT MCP Connector Requirements
- Server MUST be publicly accessible (no localhost)
- MCP endpoint typically at `/mcp` or `/mcp/`
- Health check endpoint recommended at `/`
- Use SSE or Streamable HTTP transport
- Proper initialization is critical (use `mcp.run()`, not manual uvicorn)

### 3. FastMCP Best Practices
✅ Always use `mcp.run()` for server initialization
✅ Use environment variables for port/host configuration
✅ Match FastMCP version with transport type requirements
✅ Test with MCP Inspector before deploying
✅ Use `@mcp.custom_route()` for additional HTTP endpoints

❌ Don't use `streamable_http_app()` directly with uvicorn
❌ Don't assume API compatibility across FastMCP versions
❌ Don't hardcode port/host in production code

### 4. Render Deployment Specifics
- Render automatically sets `PORT` environment variable
- Must propagate `PORT` to FastMCP via `FASTMCP_SERVER_PORT`
- Free tier has cold starts (~30 seconds)
- Build logs are essential for debugging
- Use `clearCache:"clear"` when changing dependencies

---

## Debugging Process Used

1. **Check error logs**: `mcp__render__list_logs()`
2. **Verify deployment status**: `mcp__render__get_deploy()`
3. **Test health endpoint**: `curl https://scatter-plotter-mcp.onrender.com/`
4. **Research error messages**: WebSearch for specific errors
5. **Consult documentation**: FastMCP docs, MCP specification
6. **Incremental fixes**: One issue at a time, test after each fix

---

## Final Working Configuration

**requirements.txt**:
```
fastmcp>=2.12.0
mcp>=1.2.0
pandas>=1.4.4
numpy>=1.21.5
plotly>=5.9.0
scipy>=1.8.0
openpyxl>=3.0.10
kaleido>=0.2.1
uvicorn>=0.30.0
starlette>=0.27.0
```

**mcp_server.py** (key section):
```python
@mcp.custom_route("/", methods=["GET", "HEAD"])
async def health_check(request):
    from starlette.responses import JSONResponse
    return JSONResponse({
        "name": "Scatter Plotter MCP Server",
        "status": "running",
        "mcp_endpoint": "/mcp/",
        "tools": ["upload_data", "create_scatter_plot", "list_datasets", "get_column_info"]
    })

if __name__ == "__main__":
    import os
    port = os.environ.get("PORT", "8000")
    host = os.environ.get("HOST", "0.0.0.0")

    os.environ["FASTMCP_SERVER_PORT"] = port
    os.environ["FASTMCP_SERVER_HOST"] = host

    mcp.run(transport="sse")
```

---

## Time Investment
- Total debugging time: ~2 hours
- Number of deployment attempts: 4
- Issues encountered: 3 major errors
- Solution: Progressive debugging with proper documentation research

---

## References
- FastMCP Docs: https://gofastmcp.com/
- MCP Specification: https://modelcontextprotocol.io/
- ChatGPT MCP Guide: https://gofastmcp.com/integrations/chatgpt
- GitHub Issues consulted: FastMCP #532, #737, #823
