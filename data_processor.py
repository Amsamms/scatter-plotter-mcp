"""
Data Processing Module for Scatter Plotter MCP Server
Handles data loading, validation, and preprocessing
"""

import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import base64
from typing import Tuple, Optional
import scipy.stats as stats


class DataProcessor:
    """Handle all data processing operations"""

    @staticmethod
    def load_data(data_input: str) -> pd.DataFrame:
        """
        Load data from various input formats

        Args:
            data_input: Can be CSV string, base64-encoded CSV, or base64-encoded Excel

        Returns:
            pandas DataFrame
        """
        try:
            # Try direct CSV string
            df = pd.read_csv(StringIO(data_input), encoding_errors='ignore')
            return df
        except:
            pass

        try:
            # Try base64-decoded CSV
            decoded = base64.b64decode(data_input)
            df = pd.read_csv(BytesIO(decoded), encoding_errors='ignore')
            return df
        except:
            pass

        try:
            # Try base64-decoded Excel
            decoded = base64.b64decode(data_input)
            df = pd.read_excel(BytesIO(decoded), engine='openpyxl')
            return df
        except Exception as e:
            raise ValueError(f"Could not parse data. Please provide CSV text or base64-encoded CSV/Excel. Error: {str(e)}")

    @staticmethod
    def validate_columns(df: pd.DataFrame, x_column: str, y_columns: list) -> Tuple[bool, str]:
        """
        Validate that specified columns exist in dataframe

        Args:
            df: Input dataframe
            x_column: X-axis column name
            y_columns: List of Y-axis column names

        Returns:
            Tuple of (is_valid, error_message)
        """
        if x_column not in df.columns:
            return False, f"Column '{x_column}' not found. Available columns: {list(df.columns)}"

        missing_y = [col for col in y_columns if col not in df.columns]
        if missing_y:
            return False, f"Y columns not found: {missing_y}. Available columns: {list(df.columns)}"

        return True, ""

    @staticmethod
    def convert_to_numeric(df: pd.DataFrame, columns: list, is_date: bool = False, date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Convert specified columns to numeric or datetime

        Args:
            df: Input dataframe
            columns: List of column names to convert
            is_date: Whether data contains date columns
            date_column: Name of the date column

        Returns:
            Converted dataframe
        """
        df_copy = df.copy()

        for column in columns:
            if column in df_copy.columns:
                # Check if this is the date column
                if is_date and date_column and column == date_column:
                    try:
                        df_copy[column] = pd.to_datetime(df_copy[column])
                    except:
                        # If conversion fails, keep as is
                        pass
                else:
                    # Convert to numeric
                    df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')

        return df_copy

    @staticmethod
    def remove_outliers(df: pd.DataFrame, threshold: float = 4.0) -> pd.DataFrame:
        """
        Remove outliers using Z-score method

        Args:
            df: Input dataframe
            threshold: Z-score threshold (default 4.0)

        Returns:
            Dataframe with outliers removed
        """
        try:
            df_copy = df.copy()

            # Get numeric columns only
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns

            if len(numeric_cols) == 0:
                return df_copy

            # Calculate z-scores
            z_scores = stats.zscore(df_copy[numeric_cols], nan_policy='omit')
            z_scores = pd.DataFrame(z_scores, columns=numeric_cols, index=df_copy.index)
            z_scores.fillna(0, inplace=True)

            # Filter based on threshold
            abs_z_scores = np.abs(z_scores)
            filtered_entries = (abs_z_scores < threshold).all(axis=1)

            df_filtered = df_copy[filtered_entries]

            return df_filtered
        except Exception as e:
            print(f"Warning: Outlier removal failed: {str(e)}")
            return df

    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> dict:
        """
        Get summary statistics of dataframe

        Args:
            df: Input dataframe

        Returns:
            Dictionary with summary info
        """
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "preview": df.head(5).to_dict()
        }
