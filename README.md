# Scatter Plotter MCP Server

A Model Context Protocol (MCP) server that provides interactive scatter plotting capabilities for ChatGPT and other MCP clients.

## Features

- Upload CSV/Excel data
- Create interactive scatter plots with dual Y-axes
- Time-series support for date columns
- Statistical outlier removal
- Large dataset optimization
- Multiple data series on single chart

## Tools Available

### 1. upload_data
Upload and validate your dataset. Accepts CSV text or base64-encoded CSV/Excel files.

**Parameters:**
- `data` (string): CSV text or base64-encoded data
- `name` (string, optional): Dataset name (default: "dataset")

### 2. create_scatter_plot
Create interactive scatter plots with advanced features.

**Parameters:**
- `dataset_name` (string): Name of uploaded dataset
- `x_column` (string): Column for X-axis
- `y_primary_columns` (string): Comma-separated columns for primary Y-axis
- `y_secondary_columns` (string, optional): Comma-separated columns for secondary Y-axis
- `has_date_column` (bool): Whether data contains date columns
- `date_column` (string): Name of date column
- `remove_outliers` (bool): Remove statistical outliers
- `outlier_threshold` (float): Z-score threshold (default: 4.0)
- `large_dataset` (bool): Optimize for large data (>10k points)
- `chart_title` (string, optional): Custom chart title

### 3. list_datasets
List all uploaded datasets and their columns.

### 4. get_column_info
Get detailed statistics about a specific column.

**Parameters:**
- `dataset_name` (string): Dataset name
- `column_name` (string): Column to inspect

## Local Development

### Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python mcp_server.py
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

## Deployment

### Option 1: Railway

1. Install Railway CLI:
```bash
npm install -g railway
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Get your public URL from Railway dashboard

### Option 2: Render

1. Create account at render.com
2. Connect GitHub repository
3. Create new "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python mcp_server.py`
6. Deploy and get public URL

### Option 3: Local with ngrok

1. Start server:
```bash
python mcp_server.py
```

2. In another terminal:
```bash
ngrok http 8000
```

3. Use the ngrok HTTPS URL

## ChatGPT Integration

1. Open ChatGPT
2. Go to Settings → Beta Features
3. Enable "Developer Mode"
4. Click "Add MCP Server"
5. Enter:
   - **Name**: Scatter Plotter
   - **Description**: Create interactive scatter plots from data
   - **MCP Server URL**: Your deployment URL (e.g., https://your-app.railway.app)
   - **Authentication**: OAuth (or None if not implemented)
6. Check "I trust this application"
7. Click "Create"

## Usage Example in ChatGPT

```
User: "I want to create a scatter plot"

ChatGPT: "I'll help you with that! Please provide your data as CSV."

User: [pastes CSV data]

ChatGPT: [Calls upload_data tool]
"Great! Your data has been uploaded. I see columns: Date, Sales, Revenue, Profit.
What would you like to plot?"

User: "Plot Sales and Revenue over time, with Profit on a secondary axis"

ChatGPT: [Calls create_scatter_plot with appropriate parameters]
[Displays the generated chart]
```

## Technical Details

- **Framework**: FastMCP (Python MCP SDK)
- **Plotting**: Plotly
- **Data Processing**: Pandas, NumPy, SciPy
- **Image Conversion**: Kaleido

## File Structure

```
scatter_plotter_MCP/
├── mcp_server.py          # Main MCP server
├── data_processor.py      # Data loading and preprocessing
├── plotting_engine.py     # Chart generation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── Procfile              # Deployment configuration
└── outputs/              # Temporary chart storage
```

## Environment Variables

None required for basic operation. For production:
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

## License

MIT License

## Author

Ahmed Mohamed Sabri (@amsamms)
ahmedsabri85@gmail.com
