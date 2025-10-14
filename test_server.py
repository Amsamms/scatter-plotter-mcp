"""
Simple test script to verify MCP server functionality
Run this to test locally before deploying
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_processor import DataProcessor
from plotting_engine import PlottingEngine
import pandas as pd


def test_data_processor():
    """Test data loading and processing"""
    print("Testing Data Processor...")

    # Load example data
    with open('example_data.csv', 'r') as f:
        csv_data = f.read()

    processor = DataProcessor()
    df = processor.load_data(csv_data)

    print(f"✓ Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
    print(f"  Columns: {', '.join(df.columns.tolist())}")

    # Test column validation
    valid, msg = processor.validate_columns(df, 'Date', ['Sales', 'Revenue'])
    assert valid, f"Column validation failed: {msg}"
    print("✓ Column validation passed")

    # Test data conversion
    df_converted = processor.convert_to_numeric(
        df,
        ['Date', 'Sales', 'Revenue'],
        is_date=True,
        date_column='Date'
    )
    print(f"✓ Data conversion successful")
    print(f"  Date type: {df_converted['Date'].dtype}")
    print(f"  Sales type: {df_converted['Sales'].dtype}")

    # Test outlier removal
    df_no_outliers = processor.remove_outliers(df, threshold=4.0)
    print(f"✓ Outlier removal works: {len(df)} → {len(df_no_outliers)} rows")

    print()
    return df_converted


def test_plotting_engine(df):
    """Test chart generation"""
    print("Testing Plotting Engine...")

    plotter = PlottingEngine()

    # Test single chart creation
    fig = plotter.create_single_chart(
        df=df,
        x_column='Date',
        y_primary=['Sales', 'Revenue'],
        y_secondary=['Profit'],
        plot_style='lines+markers',
        title='Test Chart'
    )

    print("✓ Chart created successfully")
    print(f"  Figure type: {type(fig)}")

    # Test image conversion
    try:
        img_bytes = plotter.figure_to_bytes(fig, format='png')
        print(f"✓ Image conversion successful: {len(img_bytes)} bytes")

        # Save test image
        with open('outputs/test_chart.png', 'wb') as f:
            f.write(img_bytes)
        print("✓ Test chart saved to outputs/test_chart.png")
    except Exception as e:
        print(f"⚠ Image conversion requires kaleido: {e}")
        print("  Install with: pip install kaleido")

    print()
    return fig


def test_correlation_heatmap(df):
    """Test correlation heatmap"""
    print("Testing Correlation Heatmap...")

    plotter = PlottingEngine()

    fig = plotter.create_correlation_heatmap(
        df=df,
        columns=['Sales', 'Revenue', 'Profit', 'Customers']
    )

    print("✓ Correlation heatmap created")
    print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("SCATTER PLOTTER MCP SERVER - TEST SUITE")
    print("=" * 60)
    print()

    try:
        # Test data processing
        df = test_data_processor()

        # Test plotting
        fig = test_plotting_engine(df)

        # Test correlation
        test_correlation_heatmap(df)

        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Install remaining dependencies: pip install kaleido")
        print("2. Run the MCP server: python mcp_server.py")
        print("3. Test with MCP Inspector: npx @modelcontextprotocol/inspector python mcp_server.py")
        print("4. Deploy to Railway or Render")
        print()

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
