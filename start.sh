#!/bin/bash

# Install Chrome for Kaleido if not already installed
echo "Checking for Chrome installation..."
if ! command -v google-chrome &> /dev/null; then
    echo "Chrome not found. Installing via kaleido..."
    python -c "import kaleido; kaleido.get_chrome_sync()" || {
        echo "Kaleido Chrome installation failed, trying plotly_get_chrome..."
        plotly_get_chrome || echo "Warning: Chrome installation failed, plots may not work"
    }
else
    echo "Chrome already installed"
fi

# Start the MCP server
echo "Starting MCP server..."
python mcp_server.py
