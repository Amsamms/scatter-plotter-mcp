# Quick Start - Scatter Plotter MCP

## 🚀 Get Started in 3 Steps

### Step 1: Setup (5 minutes)
```bash
cd /home/amsamms/projects/web_apps/scatter_plotter_MCP
source venv/bin/activate
pip install -r requirements.txt
python test_server.py
```

### Step 2: Deploy (5 minutes)
```bash
# Install Railway
npm install -g railway

# Deploy
railway login
railway init
railway up
railway domain
```

Copy your URL: `https://scatter-plotter-mcp-xxx.railway.app`

### Step 3: Connect to ChatGPT (2 minutes)

1. ChatGPT → Settings → Beta Features → Enable "Developer Mode"
2. Add MCP Server:
   - **Name**: Scatter Plotter
   - **URL**: Your Railway URL
   - **Auth**: None
3. Check "I trust this application"
4. Create!

## ✅ Test It

In ChatGPT, say:
```
"Create a scatter plot with this data:

Date,Sales,Revenue
2023-01-01,1200,15000
2023-02-01,1350,16500
2023-03-01,1100,14000

Plot Sales and Revenue over time"
```

ChatGPT will create and display your chart! 🎉

## 📚 Full Docs

- Detailed guide: `DEPLOYMENT_GUIDE.md`
- API reference: `README.md`
- Test locally: `python test_server.py`

## 🛠️ 4 Tools Available

1. **upload_data** - Upload CSV/Excel
2. **create_scatter_plot** - Create charts
3. **list_datasets** - View uploaded data
4. **get_column_info** - Column statistics

## 💡 Pro Tips

- Use time-series for date columns
- Remove outliers with `outlier_threshold`
- Add secondary Y-axis for different scales
- Enable `large_dataset` for >10k points

## 🆘 Need Help?

```bash
# Check if server works
python test_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python mcp_server.py

# View Railway logs
railway logs
```

## 🎯 What You Built

- ✅ Full MCP server with 4 tools
- ✅ Data processing & validation
- ✅ Interactive Plotly charts
- ✅ Image generation (base64)
- ✅ Railway/Render ready
- ✅ ChatGPT integration
- ✅ Production ready

**Enjoy!** 🚀
