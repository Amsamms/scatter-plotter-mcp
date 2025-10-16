# Building MCP Servers: The Working Method

**A practical guide based on real implementation experience**

Last Updated: October 2025
Author: Ahmed Mohamed Sabri (@amsamms)

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Architecture Overview](#architecture-overview)
3. [The Working Implementation Pattern](#the-working-implementation-pattern)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Deployment to Render](#deployment-to-render)
6. [ChatGPT Integration](#chatgpt-integration)
7. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
8. [Testing Your MCP Server](#testing-your-mcp-server)
9. [Templates for Different Use Cases](#templates-for-different-use-cases)

---

## What is MCP?

**Model Context Protocol (MCP)** is an open standard announced by Anthropic in November 2024 that enables AI assistants like ChatGPT and Claude to connect to external data sources and tools.

### Key Benefits:
- **Extend AI capabilities** with custom tools and data sources
- **Standardized protocol** - works across different AI platforms
- **Remote deployment** - host tools on your own servers
- **Real-time data access** - AI can fetch live data, not just training data

### Use Cases:
- 📊 **Data visualization** (scatter plots, charts, dashboards)
- 🖼️ **Photo editing** (filters, transformations, batch processing)
- 🤖 **Machine learning** (model inference, data preprocessing)
- 📁 **File operations** (document processing, format conversion)
- 🌐 **API integration** (database queries, external services)
- 🔧 **Custom workflows** (automation, data pipelines)

---

## Architecture Overview

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   ChatGPT   │ ◄────── │   MCP Server     │ ◄────── │  Your Tools │
│   Claude    │   SSE   │  (FastMCP/HTTP)  │  Python │  Functions  │
└─────────────┘         └──────────────────┘         └─────────────┘
     Client                  Transport                   Business Logic
```

### Components:
1. **MCP Client** (ChatGPT, Claude) - Makes requests to your tools
2. **MCP Server** (Your code) - Exposes tools via HTTP/SSE
3. **Transport Layer** (SSE or HTTP) - Protocol for communication
4. **Tool Functions** (Your business logic) - Actual functionality

---

## The Working Implementation Pattern

After extensive testing, here's the **proven pattern** that works reliably:

### 1. Project Structure

```
your-mcp-server/
├── mcp_server.py          # Main MCP server (entry point)
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script (optional)
├── your_module.py        # Your business logic
└── README.md             # Documentation
```

### 2. Core Dependencies

**requirements.txt** (minimum):
```txt
fastmcp>=2.12.0           # MCP server framework
mcp>=1.2.0                # MCP protocol library
uvicorn>=0.30.0           # ASGI server
starlette>=0.27.0         # Web framework
```

Add your domain-specific libraries:
```txt
# For data/plotting:
pandas>=1.4.4
plotly>=5.9.0
kaleido>=0.2.1

# For image processing:
Pillow>=9.0.0
opencv-python>=4.5.0

# For ML:
scikit-learn>=1.0.0
tensorflow>=2.8.0
torch>=1.10.0
```

### 3. MCP Server Implementation (mcp_server.py)

**THE CORRECT PATTERN:**

```python
import os
from mcp.server.fastmcp import FastMCP

# ═══════════════════════════════════════════════════════════
# CRITICAL: Read environment variables BEFORE FastMCP init
# ═══════════════════════════════════════════════════════════
port = int(os.environ.get("PORT", 8000))
host = os.environ.get("HOST", "0.0.0.0")

# ═══════════════════════════════════════════════════════════
# CRITICAL: Pass host and port to FastMCP constructor
# NOT to mcp.run() - this is the key mistake to avoid!
# ═══════════════════════════════════════════════════════════
mcp = FastMCP(
    "Your MCP Server Name",
    port=port,
    host=host,
    dependencies=["your", "required", "packages"]
)

# Import your business logic modules
from your_module import YourClass

# Initialize your modules
your_instance = YourClass()


# ═══════════════════════════════════════════════════════════
# Define Tools using @mcp.tool() decorator
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def your_tool_name(param1: str, param2: int = 10) -> str:
    """
    Clear description of what this tool does.

    IMPORTANT FOR CHATGPT: Explain any special requirements
    (e.g., "Pass actual file contents, not file paths")

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 10)

    Returns:
        Description of what the tool returns

    Example:
        your_tool_name("input", 20)
    """
    try:
        # Your business logic here
        result = your_instance.process(param1, param2)
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# ═══════════════════════════════════════════════════════════
# Health Check Endpoint (required for monitoring)
# ═══════════════════════════════════════════════════════════

@mcp.custom_route("/", methods=["GET", "HEAD"])
async def health_check(request):
    """Health check endpoint for Render and monitoring"""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "name": "Your MCP Server Name",
        "status": "running",
        "version": "1.0.0",
        "transport": "sse",
        "mcp_endpoint": "/sse",
        "tools": ["tool1", "tool2", "tool3"],
        "chatgpt_connector_url": f"https://your-server.onrender.com/sse"
    })


# ═══════════════════════════════════════════════════════════
# Server Startup
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Starting MCP server on {host}:{port}")
    print(f"SSE endpoint: http://{host}:{port}/sse")
    print(f"Health check: http://{host}:{port}/")

    # CRITICAL: Use "sse" transport for ChatGPT
    # DO NOT pass host/port here - already set in constructor
    mcp.run(transport="sse")
```

### Key Points:

✅ **DO:**
- Read `PORT` and `HOST` from environment at module level
- Pass `host` and `port` to `FastMCP()` constructor
- Use `transport="sse"` for ChatGPT compatibility
- Include health check endpoint at `/`
- Document tool parameters clearly
- Handle errors gracefully in tools

❌ **DON'T:**
- Pass `host`/`port` to `mcp.run()` - causes TypeError
- Use `transport="http"` - not supported in older FastMCP versions
- Use `streamable_http_app()` + `uvicorn.run()` - causes RuntimeError
- Assume ChatGPT can access file paths - it can't
- Forget to handle exceptions in tools

---

## Step-by-Step Guide

### Phase 1: Local Development

#### Step 1: Create Project Structure

```bash
mkdir my-mcp-server
cd my-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create files
touch mcp_server.py requirements.txt README.md
```

#### Step 2: Install Dependencies

```bash
pip install fastmcp>=2.12.0 mcp>=1.2.0 uvicorn starlette
pip install <your-domain-specific-packages>

# Save dependencies
pip freeze > requirements.txt
```

#### Step 3: Implement Your Tools

Create your business logic modules (separate from MCP server):

```python
# your_module.py
class YourProcessor:
    def __init__(self):
        # Initialize your resources
        pass

    def process(self, data):
        # Your actual functionality
        return processed_data
```

#### Step 4: Create MCP Server

Use the pattern from section 3 above, implementing your tools with `@mcp.tool()`.

#### Step 5: Test Locally

```bash
# Run the server
python mcp_server.py

# Test health check (in another terminal)
curl http://localhost:8000/

# Test SSE endpoint
curl http://localhost:8000/sse
```

### Phase 2: GitHub Setup

#### Step 6: Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: MCP server implementation"
```

#### Step 7: Create GitHub Repository

```bash
# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/your-mcp-server.git
git branch -M master  # or main
git push -u origin master
```

### Phase 3: Deployment to Render

#### Step 8: Create Render Account

1. Go to https://render.com
2. Sign up (free tier available)
3. Connect your GitHub account

#### Step 9: Create Web Service

**Option A: Using Render Dashboard**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `your-mcp-server`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python mcp_server.py`
   - **Plan**: Free
4. Click "Create Web Service"

**Option B: Using Claude Code with Render MCP** (if available)
```bash
# In Claude Code, use Render MCP to create service
# This is faster and automated
```

#### Step 10: Configure Environment Variables (if needed)

In Render dashboard:
1. Go to "Environment" tab
2. Add any secrets/API keys your server needs
3. Render automatically provides `PORT` (10000 on free tier)

#### Step 11: Monitor Deployment

1. Watch build logs in Render dashboard
2. Wait for "Your service is live" message
3. Note your URL: `https://your-mcp-server.onrender.com`

#### Step 12: Verify Deployment

```bash
# Test health check
curl https://your-mcp-server.onrender.com/

# Test SSE endpoint
curl https://your-mcp-server.onrender.com/sse
```

---

## ChatGPT Integration

### Step 1: Enable Developer Mode

1. Open ChatGPT at https://chatgpt.com
2. Click your profile icon (bottom left)
3. Go to **Settings** → **Connectors** → **Advanced**
4. Toggle **Developer Mode** ON

### Step 2: Add MCP Connector

1. In the Connectors tab, click **Add Connector**
2. Enter your SSE endpoint URL:
   ```
   https://your-mcp-server.onrender.com/sse
   ```
3. Click **Add** or **Connect**
4. Wait for connection confirmation

### Step 3: Test the Connection

Start a new chat and try:
```
What tools do you have available?
```

You should see your tools listed!

### Step 4: Use Your Tools

Example usage:
```
Please use the upload_data tool with this CSV:
[paste your data]

Then create a visualization using the create_plot tool.
```

---

## Common Pitfalls & Solutions

### Issue 1: TypeError - FastMCP.run() got unexpected keyword 'host'

❌ **Wrong:**
```python
mcp = FastMCP("Server")
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

✅ **Correct:**
```python
mcp = FastMCP("Server", host="0.0.0.0", port=8000)
mcp.run(transport="sse")
```

### Issue 2: ValueError - Unknown transport: http

❌ **Wrong:**
```python
mcp.run(transport="http")  # Not supported in older versions
```

✅ **Correct:**
```python
# Upgrade FastMCP first
pip install fastmcp>=2.12.0

# Then use SSE
mcp.run(transport="sse")
```

### Issue 3: RuntimeError - Task group is not initialized

❌ **Wrong:**
```python
app = mcp.streamable_http_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

✅ **Correct:**
```python
# Use mcp.run() directly
mcp.run(transport="sse")
```

### Issue 4: Port Detection Failed on Render

❌ **Wrong:**
```python
# Using localhost or wrong host
mcp = FastMCP("Server", host="127.0.0.1", port=8000)
```

✅ **Correct:**
```python
# Must bind to 0.0.0.0 and use PORT from environment
port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Server", host="0.0.0.0", port=port)
```

### Issue 5: ChatGPT Passing File Paths Instead of Contents

❌ **Problem:**
```
Tool receives: "/mnt/data/file.xlsx"
Can't read: Not accessible from MCP server
```

✅ **Solution:**
```python
@mcp.tool()
def upload_data(data: str) -> str:
    """
    IMPORTANT FOR CHATGPT: Do NOT pass file paths!
    Read the file contents first, then pass the actual data.

    For Excel files: Read and convert to CSV text first.
    """
    # Now data contains actual contents
```

### Issue 6: Kaleido Requires Chrome (for Plotly)

❌ **Error:**
```
RuntimeError: Kaleido requires Google Chrome to be installed
```

✅ **Solution:**
```python
# Auto-install Chrome on first use
try:
    return fig.to_image(format='png', engine='kaleido')
except Exception as e:
    if 'Chrome' in str(e):
        import kaleido
        kaleido.get_chrome_sync()
        return fig.to_image(format='png', engine='kaleido')
    raise
```

---

## Testing Your MCP Server

### Local Testing

```bash
# 1. Start server
python mcp_server.py

# 2. Test health check
curl http://localhost:8000/

# 3. Test SSE stream
curl -N http://localhost:8000/sse
```

### Remote Testing (Render)

```bash
# Health check
curl https://your-server.onrender.com/

# SSE endpoint
curl -N https://your-server.onrender.com/sse
```

### ChatGPT Testing Checklist

- [ ] Tools appear when asking "What tools do you have?"
- [ ] Tool descriptions are clear and helpful
- [ ] Parameters are correctly understood
- [ ] Tool executes without errors
- [ ] Results are properly formatted
- [ ] Error messages are helpful

---

## Templates for Different Use Cases

### Template 1: Data Processing MCP

```python
import os
from mcp.server.fastmcp import FastMCP
import pandas as pd

port = int(os.environ.get("PORT", 8000))
host = os.environ.get("HOST", "0.0.0.0")

mcp = FastMCP("Data Processor", port=port, host=host)

@mcp.tool()
def process_csv(csv_data: str, operation: str) -> str:
    """
    Process CSV data with various operations.

    Args:
        csv_data: CSV text (not file path!)
        operation: clean, summarize, transform

    Returns:
        Processed data summary
    """
    try:
        df = pd.read_csv(io.StringIO(csv_data))

        if operation == "clean":
            df = df.dropna()
        elif operation == "summarize":
            return df.describe().to_string()

        return f"Processed {len(df)} rows successfully"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
```

### Template 2: Image Processing MCP

```python
import os
from mcp.server.fastmcp import FastMCP
from PIL import Image
import io
import base64

port = int(os.environ.get("PORT", 8000))
host = os.environ.get("HOST", "0.0.0.0")

mcp = FastMCP("Image Processor", port=port, host=host)

@mcp.tool()
def apply_filter(image_base64: str, filter_type: str) -> str:
    """
    Apply filters to images.

    Args:
        image_base64: Base64-encoded image data
        filter_type: grayscale, blur, sharpen, rotate

    Returns:
        Base64-encoded processed image
    """
    try:
        # Decode image
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))

        # Apply filter
        if filter_type == "grayscale":
            image = image.convert("L")
        elif filter_type == "rotate":
            image = image.rotate(90)

        # Encode result
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        result = base64.b64encode(buffer.getvalue()).decode()

        return result
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
```

### Template 3: Machine Learning MCP

```python
import os
from mcp.server.fastmcp import FastMCP
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

port = int(os.environ.get("PORT", 8000))
host = os.environ.get("HOST", "0.0.0.0")

mcp = FastMCP("ML Predictor", port=port, host=host)

# Load pre-trained model (saved during deployment)
model = joblib.load('model.pkl')

@mcp.tool()
def predict(features: str) -> str:
    """
    Make predictions using trained ML model.

    Args:
        features: CSV with feature columns

    Returns:
        Predictions as JSON
    """
    try:
        # Parse features
        df = pd.read_csv(io.StringIO(features))

        # Predict
        predictions = model.predict(df)

        return {
            "predictions": predictions.tolist(),
            "count": len(predictions)
        }
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
```

---

## Best Practices

### 1. Documentation
- Write clear tool descriptions
- Include examples in docstrings
- Document parameter types and formats
- Explain what the tool returns

### 2. Error Handling
- Always wrap tool logic in try/except
- Return helpful error messages
- Log errors for debugging
- Don't expose sensitive information

### 3. Performance
- Keep tools fast (< 30 seconds)
- Use caching for expensive operations
- Return progress updates for long tasks
- Consider async operations

### 4. Security
- Validate all inputs
- Sanitize user data
- Don't execute arbitrary code
- Use environment variables for secrets

### 5. Deployment
- Test locally first
- Use health checks
- Monitor logs
- Set up auto-deploy from GitHub

---

## Resources

### Official Documentation
- MCP Specification: https://modelcontextprotocol.io/
- FastMCP Docs: https://gofastmcp.com/
- Render Docs: https://render.com/docs

### Community
- FastMCP GitHub: https://github.com/jlowin/fastmcp
- MCP Examples: https://github.com/topics/mcp-server

### Related Tools
- Claude Code: CLI for development
- Render MCP: Server management
- ChatGPT Developer Mode: MCP testing

---

## Appendix: Complete Working Example

See the **Scatter Plotter MCP** in this repository for a complete, production-ready example that includes:

- ✅ Data upload and validation
- ✅ Interactive plotting with Plotly
- ✅ Date handling and outlier removal
- ✅ Auto-install dependencies (Chrome for Kaleido)
- ✅ Comprehensive error handling
- ✅ Deployed on Render
- ✅ Integrated with ChatGPT

Files to study:
- `mcp_server.py` - Main server implementation
- `data_processor.py` - Business logic module
- `plotting_engine.py` - Visualization engine
- `requirements.txt` - Dependencies
- `mistakes.md` - What NOT to do

---

## Quick Reference Card

```bash
# Create MCP server
mkdir my-mcp && cd my-mcp
python -m venv venv && source venv/bin/activate
pip install fastmcp>=2.12.0 mcp uvicorn starlette

# Basic structure
import os
from mcp.server.fastmcp import FastMCP

port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Name", port=port, host="0.0.0.0")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"

if __name__ == "__main__":
    mcp.run(transport="sse")

# Deploy to Render
git init && git add . && git commit -m "Initial"
git remote add origin <your-repo>
git push -u origin master

# Connect to ChatGPT
URL: https://your-server.onrender.com/sse
```

---

## Changelog

- **Oct 2025**: Initial version based on Scatter Plotter MCP implementation
- Verified with FastMCP 2.12.4, ChatGPT Developer Mode
- Tested on Render free tier

---

**Next Steps**: Use this guide to build your next MCP server! Whether it's photo editing, machine learning, or any custom functionality - the pattern is the same. Good luck! 🚀
