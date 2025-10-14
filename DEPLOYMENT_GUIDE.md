# Scatter Plotter MCP - Complete Deployment Guide

## Quick Start Summary

Your MCP server is ready! Here's what was created:

```
scatter_plotter_MCP/
├── mcp_server.py          # Main MCP server (4 tools)
├── data_processor.py      # Data handling
├── plotting_engine.py     # Chart generation
├── requirements.txt       # Dependencies
├── test_server.py         # Testing script
├── example_data.csv       # Sample data
├── Procfile              # Railway/Render config
├── railway.json          # Railway config
├── render.yaml           # Render config
└── outputs/              # Chart output folder
```

---

## Step 1: Local Setup & Testing

### 1.1 Install Dependencies

```bash
cd /home/amsamms/projects/web_apps/scatter_plotter_MCP

# Activate virtual environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# This installs:
# - fastmcp (MCP framework)
# - mcp (MCP protocol)
# - pandas, numpy (data processing)
# - plotly (charts)
# - scipy (statistics)
# - kaleido (image conversion)
# - openpyxl (Excel support)
```

### 1.2 Run Tests

```bash
# Test the core functionality
python test_server.py

# Expected output:
# ✓ Data loaded successfully
# ✓ Column validation passed
# ✓ Chart created successfully
# ✓ Image conversion successful
```

### 1.3 Test MCP Server Locally

```bash
# Start the MCP server
python mcp_server.py

# The server will start and wait for MCP client connections
```

### 1.4 Test with MCP Inspector (Optional but Recommended)

Open another terminal:

```bash
# Install MCP Inspector (one-time)
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector python mcp_server.py

# This opens a web interface where you can:
# - See all available tools
# - Test tool calls
# - View responses
# - Debug issues
```

---

## Step 2: Deploy to Cloud

### Option A: Deploy to Railway (Recommended - Easiest)

#### 2.1 Install Railway CLI

```bash
npm install -g railway
```

#### 2.2 Login to Railway

```bash
railway login
```

This opens your browser to authenticate.

#### 2.3 Initialize and Deploy

```bash
cd /home/amsamms/projects/web_apps/scatter_plotter_MCP

# Initialize Railway project
railway init

# When prompted:
# - Project name: scatter-plotter-mcp
# - Start command: (leave default, uses Procfile)

# Deploy!
railway up
```

#### 2.4 Get Your Public URL

```bash
# Generate public domain
railway domain

# Or view in dashboard
railway open
```

Your URL will be something like: `https://scatter-plotter-mcp.railway.app`

#### 2.5 Set as Production

```bash
railway environment production
railway up
```

---

### Option B: Deploy to Render

#### 2.1 Prepare Repository

1. Initialize git (if not already):
```bash
cd /home/amsamms/projects/web_apps/scatter_plotter_MCP
git init
git add .
git commit -m "Initial commit - Scatter Plotter MCP Server"
```

2. Create GitHub repository and push:
```bash
gh repo create scatter-plotter-mcp --public --source=. --push
```

#### 2.2 Deploy on Render

1. Go to https://render.com
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: scatter-plotter-mcp
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python mcp_server.py`
   - **Plan**: Free
6. Click "Create Web Service"

#### 2.3 Get Your URL

After deployment completes, your URL will be:
`https://scatter-plotter-mcp.onrender.com`

---

### Option C: Local with ngrok (For Testing Only)

#### 2.1 Install ngrok

```bash
npm install -g ngrok
# Or: snap install ngrok
```

#### 2.2 Start Server and Tunnel

Terminal 1:
```bash
cd /home/amsamms/projects/web_apps/scatter_plotter_MCP
source venv/bin/activate
python mcp_server.py
```

Terminal 2:
```bash
ngrok http 8000
```

Copy the HTTPS URL from ngrok (e.g., `https://abc123.ngrok.io`)

**Note**: ngrok URLs change each time you restart, so this is only for testing!

---

## Step 3: Connect to ChatGPT

### 3.1 Enable Developer Mode in ChatGPT

1. Open ChatGPT (web or desktop app)
2. Click your profile → Settings
3. Go to "Beta Features"
4. Enable "Developer Mode"

### 3.2 Add MCP Server

1. In ChatGPT settings, find "MCP Servers" or "Connectors"
2. Click "Add MCP Server" or "New Connector"
3. Fill in:

```
Name: Scatter Plotter
Description: Create interactive scatter plots from CSV/Excel data
MCP Server URL: https://your-deployment-url.railway.app
Authentication: None (or OAuth if you added it)
```

4. Check "I trust this application"
5. Click "Create" or "Add"

### 3.3 Verify Connection

In ChatGPT, type:
```
"List available scatter plotter tools"
```

ChatGPT should show the 4 available tools:
- upload_data
- create_scatter_plot
- list_datasets
- get_column_info

---

## Step 4: Use in ChatGPT

### Example Conversation

**User**: "I want to create a scatter plot of my sales data"

**ChatGPT**: "I can help you with that! Please provide your data. You can paste CSV data directly or describe what you have."

**User**:
```csv
Date,Sales,Revenue,Profit
2023-01-01,1200,15000,3000
2023-02-01,1350,16500,3300
2023-03-01,1100,14000,2800
...
```

**ChatGPT**: [Calls upload_data tool]
"Great! I've uploaded your data. I see 3 columns: Date, Sales, Revenue, Profit with 12 rows. What would you like to visualize?"

**User**: "Plot Sales and Revenue over time"

**ChatGPT**: [Calls create_scatter_plot tool]
[Displays interactive chart with Sales and Revenue plotted against Date]

"Here's your time-series chart! Would you like me to:
- Add Profit on a secondary axis?
- Remove any outliers?
- Create additional visualizations?"

---

## Tools Reference

### 1. upload_data
Upload CSV/Excel data for analysis.

**Parameters**:
- `data` (string): CSV text or base64-encoded file
- `name` (string, optional): Dataset name (default: "dataset")

**Example in ChatGPT**:
"Upload this data: [paste CSV]"

---

### 2. create_scatter_plot
Create interactive scatter plot.

**Parameters**:
- `dataset_name` (string): Dataset to use
- `x_column` (string): X-axis column (REQUIRED)
- `y_primary_columns` (string): Comma-separated Y columns (REQUIRED)
- `y_secondary_columns` (string): Secondary Y-axis columns
- `has_date_column` (bool): True if time-series
- `date_column` (string): Date column name
- `remove_outliers` (bool): Remove outliers
- `outlier_threshold` (float): Z-score threshold (default: 4.0)
- `large_dataset` (bool): Optimize for >10k points
- `chart_title` (string): Custom title

**Example in ChatGPT**:
"Plot Sales and Revenue against Date, with Profit on secondary axis"

ChatGPT will automatically:
- Set x_column = "Date"
- Set y_primary_columns = "Sales,Revenue"
- Set y_secondary_columns = "Profit"
- Set has_date_column = true
- Set date_column = "Date"

---

### 3. list_datasets
See all uploaded datasets.

**Example**: "What datasets do I have?"

---

### 4. get_column_info
Get statistics for a column.

**Parameters**:
- `dataset_name` (string): Dataset name
- `column_name` (string): Column to inspect

**Example**: "Show me stats for the Sales column"

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "kaleido not found" when generating images

**Solution**:
```bash
pip install kaleido
```

### Issue: Railway deployment fails

**Solution**:
- Check logs: `railway logs`
- Verify requirements.txt has all dependencies
- Ensure runtime.txt specifies Python 3.10+

### Issue: ChatGPT can't connect to MCP server

**Solution**:
- Verify URL is HTTPS (not HTTP)
- Check deployment logs for errors
- Ensure server is running
- Test with MCP Inspector first

### Issue: "Column not found" errors

**Solution**:
- Use `list_datasets` to see available columns
- Use `get_column_info` to inspect data
- Check spelling and case sensitivity

### Issue: Charts not displaying

**Solution**:
- Ensure kaleido is installed
- Check server logs for errors
- Verify data has been uploaded first

---

## Environment Variables (Optional)

For production deployments, you can set:

```bash
# Railway
railway variables set PORT=8000
railway variables set HOST=0.0.0.0

# Render
# Set in dashboard under "Environment"
PORT=8000
HOST=0.0.0.0
```

---

## Monitoring & Logs

### Railway
```bash
railway logs
railway logs --tail 100
```

### Render
- View logs in dashboard
- Or use Render CLI

### Local
```bash
# Run with verbose logging
python mcp_server.py --verbose
```

---

## Next Steps: Add More Features

To expand beyond the single chart type:

1. **Add correlation heatmap tool** in mcp_server.py
2. **Add multiple charts tool** to create separate charts
3. **Add re-scaling tool** for normalized comparisons
4. **Add export tool** to save charts as files

Example new tool:
```python
@mcp.tool()
def create_correlation_heatmap(
    dataset_name: str = "dataset",
    columns: str = ""
) -> list:
    """Create correlation heatmap"""
    # Implementation here
    pass
```

---

## Support

- GitHub Issues: https://github.com/amsamms/scatter-plotter-mcp
- Email: ahmedsabri85@gmail.com
- MCP Documentation: https://modelcontextprotocol.io

---

## Success Checklist

- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`python test_server.py`)
- [ ] Server runs locally (`python mcp_server.py`)
- [ ] Deployed to Railway or Render
- [ ] Public HTTPS URL obtained
- [ ] MCP connector added to ChatGPT
- [ ] Successfully created first chart in ChatGPT

---

## Summary

You now have a fully functional MCP server that:
- ✅ Accepts CSV/Excel data
- ✅ Creates interactive scatter plots
- ✅ Handles time-series data
- ✅ Removes outliers
- ✅ Supports dual Y-axes
- ✅ Returns images to ChatGPT
- ✅ Deployed and accessible via HTTPS

Enjoy creating beautiful charts with ChatGPT! 🎉
