"""
Scatter Plotter MCP Server
A Model Context Protocol server for creating interactive scatter plots from data
"""

import sys
import json
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
import traceback

from data_processor import DataProcessor
from plotting_engine import PlottingEngine


# Initialize FastMCP server
mcp = FastMCP("Scatter Plotter", dependencies=["pandas", "plotly", "scipy", "numpy"])

# Initialize modules
data_processor = DataProcessor()
plotting_engine = PlottingEngine()

# Store current session data (in production, use proper session management)
session_data = {}


@mcp.tool()
def upload_data(data: str, name: str = "dataset") -> str:
    """
    Upload and validate CSV or Excel data for plotting.

    This is the first step - upload your data before creating plots.
    Data can be provided as:
    - CSV text directly
    - Base64-encoded CSV
    - Base64-encoded Excel file

    Args:
        data: CSV text or base64-encoded data
        name: Name for this dataset (default: "dataset")

    Returns:
        Summary of the uploaded data including columns, rows, and preview
    """
    try:
        # Load the data
        df = data_processor.load_data(data)

        # Store in session
        session_data[name] = df

        # Get summary
        summary = data_processor.get_data_summary(df)

        # Format response
        response = f"""Data uploaded successfully!

Dataset: {name}
Rows: {summary['rows']:,}
Columns: {summary['columns']}

Available columns:
{chr(10).join(f'  - {col} ({dtype})' for col, dtype in summary['dtypes'].items())}

Data preview (first 5 rows):
{df.head(5).to_string()}

Next steps:
- Use 'create_scatter_plot' to visualize your data
- Specify which columns to use for X and Y axes
- Optionally remove outliers or handle date columns
"""

        return response

    except Exception as e:
        return f"Error uploading data: {str(e)}\n\nPlease provide data as CSV text or base64-encoded CSV/Excel."


@mcp.tool()
def create_scatter_plot(
    dataset_name: str = "dataset",
    x_column: str = "",
    y_primary_columns: str = "",
    y_secondary_columns: str = "",
    has_date_column: bool = False,
    date_column: str = "",
    remove_outliers: bool = False,
    outlier_threshold: float = 4.0,
    large_dataset: bool = False,
    chart_title: str = ""
) -> list:
    """
    Create an interactive scatter plot with dual Y-axes.

    This tool creates a single chart that can display multiple data series
    on primary and secondary Y-axes. Perfect for comparing different metrics.

    Args:
        dataset_name: Name of the uploaded dataset (default: "dataset")
        x_column: Column name for X-axis (REQUIRED)
        y_primary_columns: Comma-separated column names for primary Y-axis (REQUIRED)
        y_secondary_columns: Comma-separated column names for secondary Y-axis (optional)
        has_date_column: Set to true if your data contains date/time columns
        date_column: Name of the date column (if has_date_column is true)
        remove_outliers: Remove statistical outliers from the data
        outlier_threshold: Z-score threshold for outlier removal (default: 4.0)
        large_dataset: Enable optimization for datasets with >10,000 points
        chart_title: Custom title for the chart (optional)

    Returns:
        The scatter plot as an image that can be displayed

    Example:
        To plot Sales and Revenue against Date:
        - x_column: "Date"
        - y_primary_columns: "Sales,Revenue"
        - has_date_column: true
        - date_column: "Date"
    """
    try:
        # Validate inputs
        if not x_column:
            return [TextContent(
                type="text",
                text="Error: x_column is required. Please specify which column to use for the X-axis."
            )]

        if not y_primary_columns:
            return [TextContent(
                type="text",
                text="Error: y_primary_columns is required. Please specify at least one column for the Y-axis."
            )]

        # Get dataset
        if dataset_name not in session_data:
            return [TextContent(
                type="text",
                text=f"Error: Dataset '{dataset_name}' not found. Please upload data first using 'upload_data'."
            )]

        df = session_data[dataset_name].copy()

        # Parse column lists
        y_primary = [col.strip() for col in y_primary_columns.split(',') if col.strip()]
        y_secondary = [col.strip() for col in y_secondary_columns.split(',') if col.strip()] if y_secondary_columns else []

        # Validate columns exist
        all_columns = [x_column] + y_primary + y_secondary
        valid, error_msg = data_processor.validate_columns(df, x_column, y_primary + y_secondary)
        if not valid:
            return [TextContent(type="text", text=f"Error: {error_msg}")]

        # Remove outliers if requested
        original_rows = len(df)
        if remove_outliers:
            df = data_processor.remove_outliers(df, threshold=outlier_threshold)
            removed = original_rows - len(df)
            if removed > 0:
                print(f"Removed {removed} outliers ({removed/original_rows*100:.1f}%)")

        # Convert columns to appropriate types
        df = data_processor.convert_to_numeric(
            df,
            all_columns,
            is_date=has_date_column,
            date_column=date_column if has_date_column else None
        )

        # Determine plot style
        plot_style = 'lines+markers' if has_date_column else 'markers'

        # Create the chart
        fig = plotting_engine.create_single_chart(
            df=df,
            x_column=x_column,
            y_primary=y_primary,
            y_secondary=y_secondary if y_secondary else None,
            plot_style=plot_style,
            large_data=large_dataset,
            title=chart_title if chart_title else None
        )

        # Convert to image bytes
        img_bytes = plotting_engine.figure_to_bytes(fig, format='png')

        # Create response with image and info
        info_text = f"""Chart created successfully!

Dataset: {dataset_name}
X-axis: {x_column}
Primary Y-axis: {', '.join(y_primary)}
{"Secondary Y-axis: " + ', '.join(y_secondary) if y_secondary else ""}
Data points: {len(df):,}
{"Outliers removed: " + str(removed) + f" ({removed/original_rows*100:.1f}%)" if remove_outliers and removed > 0 else ""}

The chart shows your data as {"a time-series plot" if has_date_column else "a scatter plot"} with interactive features:
- Hover over points to see values
- Zoom in/out using the toolbar
- Pan across the chart
- Download the image
"""

        return [
            TextContent(type="text", text=info_text),
            ImageContent(type="image", data=img_bytes, mimeType="image/png")
        ]

    except Exception as e:
        error_trace = traceback.format_exc()
        return [TextContent(
            type="text",
            text=f"Error creating chart: {str(e)}\n\nDetails:\n{error_trace}"
        )]


@mcp.tool()
def list_datasets() -> str:
    """
    List all currently uploaded datasets and their columns.

    Use this to see what data is available for plotting.

    Returns:
        List of datasets with their columns
    """
    if not session_data:
        return "No datasets uploaded yet. Use 'upload_data' to upload your data."

    result = "Available datasets:\n\n"
    for name, df in session_data.items():
        result += f"Dataset: {name}\n"
        result += f"  Rows: {len(df):,}\n"
        result += f"  Columns: {', '.join(df.columns.tolist())}\n\n"

    return result


@mcp.tool()
def get_column_info(dataset_name: str = "dataset", column_name: str = "") -> str:
    """
    Get detailed information about a specific column.

    Useful for understanding your data before plotting.

    Args:
        dataset_name: Name of the dataset (default: "dataset")
        column_name: Name of the column to inspect (REQUIRED)

    Returns:
        Statistical summary and information about the column
    """
    try:
        if dataset_name not in session_data:
            return f"Error: Dataset '{dataset_name}' not found."

        if not column_name:
            return "Error: column_name is required."

        df = session_data[dataset_name]

        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found. Available: {', '.join(df.columns)}"

        col_data = df[column_name]

        result = f"Column: {column_name}\n"
        result += f"Data type: {col_data.dtype}\n"
        result += f"Non-null count: {col_data.count():,} / {len(col_data):,}\n"
        result += f"Missing values: {col_data.isnull().sum():,}\n\n"

        if col_data.dtype in ['int64', 'float64']:
            result += "Statistics:\n"
            result += f"  Mean: {col_data.mean():.2f}\n"
            result += f"  Median: {col_data.median():.2f}\n"
            result += f"  Std Dev: {col_data.std():.2f}\n"
            result += f"  Min: {col_data.min():.2f}\n"
            result += f"  Max: {col_data.max():.2f}\n"
        else:
            result += f"Unique values: {col_data.nunique()}\n"
            if col_data.nunique() <= 10:
                result += f"Values: {', '.join(str(v) for v in col_data.unique())}\n"

        result += f"\nSample values:\n{col_data.head(5).to_string()}"

        return result

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run the server with Streamable HTTP transport
    import os

    # Set port via environment variable (FastMCP reads this automatically)
    port = os.environ.get("PORT", "8000")
    os.environ["PORT"] = port

    print(f"Starting MCP server on port {port}")
    print(f"FastMCP will bind to 0.0.0.0:{port} automatically")

    # Run with Streamable HTTP transport
    # FastMCP automatically reads PORT environment variable for binding
    mcp.run(transport="streamable-http", mount_path="/mcp")
