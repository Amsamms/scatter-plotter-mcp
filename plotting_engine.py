"""
Plotting Engine Module for Scatter Plotter MCP Server
Handles chart generation using Plotly
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List


class PlottingEngine:
    """Handle all chart creation operations"""

    @staticmethod
    def create_single_chart(
        df: pd.DataFrame,
        x_column: str,
        y_primary: List[str],
        y_secondary: Optional[List[str]] = None,
        plot_style: str = 'markers',
        large_data: bool = False,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create a single chart with dual Y-axes

        Args:
            df: Input dataframe
            x_column: Column name for X-axis
            y_primary: List of columns for primary Y-axis
            y_secondary: List of columns for secondary Y-axis
            plot_style: 'markers' or 'lines+markers'
            large_data: Use Scattergl for large datasets
            title: Chart title

        Returns:
            Plotly Figure object
        """
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add primary Y-axis traces
        for column in y_primary:
            if large_data:
                fig.add_trace(
                    go.Scattergl(
                        x=df[x_column],
                        y=df[column],
                        mode=plot_style,
                        name=column
                    ),
                    secondary_y=False
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df[x_column],
                        y=df[column],
                        mode=plot_style,
                        name=column
                    ),
                    secondary_y=False
                )

        # Add secondary Y-axis traces if provided
        if y_secondary:
            for column in y_secondary:
                if large_data:
                    fig.add_trace(
                        go.Scattergl(
                            x=df[x_column],
                            y=df[column],
                            mode=plot_style,
                            name=column
                        ),
                        secondary_y=True
                    )
                else:
                    fig.add_trace(
                        go.Scatter(
                            x=df[x_column],
                            y=df[column],
                            mode=plot_style,
                            name=column
                        ),
                        secondary_y=True
                    )

        # Update layout
        fig.update_layout(
            title=title or f"{', '.join(y_primary)} vs {x_column}",
            xaxis_title=x_column,
            hovermode='x unified',
            template='plotly_white',
            width=1200,
            height=700,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Update axes labels
        if y_primary:
            fig.update_yaxes(title_text=', '.join(y_primary), secondary_y=False)
        if y_secondary:
            fig.update_yaxes(title_text=', '.join(y_secondary), secondary_y=True)

        return fig

    @staticmethod
    def create_correlation_heatmap(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create correlation heatmap

        Args:
            df: Input dataframe
            columns: Specific columns to include (None = all numeric columns)
            title: Chart title

        Returns:
            Plotly Figure object
        """
        # Select columns
        if columns:
            df_corr = df[columns]
        else:
            df_corr = df.select_dtypes(include=['number'])

        # Calculate correlation
        corr = df_corr.corr()

        # Create heatmap
        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                x=corr.columns,
                y=corr.index,
                z=corr.values,
                colorscale='RdBu',
                zmid=0,
                text=corr.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            )
        )

        fig.update_layout(
            title=title or "Correlation Heatmap",
            xaxis_title="Variables",
            yaxis_title="Variables",
            width=1000,
            height=900,
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_top_correlations_chart(
        df: pd.DataFrame,
        x_column: str,
        target_column: str,
        num_correlations: int = 3,
        plot_style: str = 'markers',
        large_data: bool = False
    ) -> List[go.Figure]:
        """
        Create charts showing top N correlations for a target column

        Args:
            df: Input dataframe
            x_column: Column for X-axis in plots
            target_column: Column to find correlations for
            num_correlations: Number of top correlations to show
            plot_style: 'markers' or 'lines+markers'
            large_data: Use Scattergl for large datasets

        Returns:
            List of Plotly Figure objects
        """
        # Get numeric columns only
        df_numeric = df.select_dtypes(include=['number'])

        # Calculate correlation matrix
        corr = df_numeric.corr()

        if target_column not in corr.columns:
            raise ValueError(f"Column '{target_column}' not found in numeric columns")

        # Find top correlations (excluding the column itself)
        correlations = corr[target_column].drop(labels=[target_column]).dropna()
        top_correlations = correlations.reindex(
            correlations.abs().sort_values(ascending=False).index
        ).head(num_correlations)

        # Create individual plots
        figures = []
        for corr_column, corr_value in top_correlations.items():
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Add target column (primary y-axis)
            if large_data:
                fig.add_trace(
                    go.Scattergl(
                        x=df[x_column],
                        y=df[target_column],
                        mode=plot_style,
                        name=target_column,
                        line=dict(color='blue')
                    ),
                    secondary_y=False
                )

                # Add correlated column (secondary y-axis)
                fig.add_trace(
                    go.Scattergl(
                        x=df[x_column],
                        y=df[corr_column],
                        mode=plot_style,
                        name=corr_column,
                        line=dict(color='red', dash='dot')
                    ),
                    secondary_y=True
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df[x_column],
                        y=df[target_column],
                        mode=plot_style,
                        name=target_column,
                        line=dict(color='blue')
                    ),
                    secondary_y=False
                )

                # Add correlated column (secondary y-axis)
                fig.add_trace(
                    go.Scatter(
                        x=df[x_column],
                        y=df[corr_column],
                        mode=plot_style,
                        name=corr_column,
                        line=dict(color='red', dash='dot')
                    ),
                    secondary_y=True
                )

            # Update layout
            fig.update_layout(
                title=f"{target_column} vs {corr_column}<br>Correlation: {corr_value:.3f}",
                xaxis_title=x_column,
                width=1200,
                height=600,
                template='plotly_white',
                legend_title="Columns"
            )

            fig.update_yaxes(title_text=f"<b>{target_column}</b>", secondary_y=False)
            fig.update_yaxes(title_text=f"<b>{corr_column}</b>", secondary_y=True)

            figures.append(fig)

        return figures

    @staticmethod
    def figure_to_bytes(fig: go.Figure, format: str = 'png') -> bytes:
        """
        Convert Plotly figure to image bytes
        Auto-installs Chrome for Kaleido if needed

        Args:
            fig: Plotly figure
            format: Image format ('png', 'jpg', 'svg')

        Returns:
            Image bytes
        """
        try:
            # Try to render the image
            return fig.to_image(format=format, engine='kaleido')
        except Exception as e:
            # If Chrome is missing, install it automatically
            if 'Chrome' in str(e) or 'chrome' in str(e):
                print("Chrome not found. Installing Chrome for Kaleido...")
                try:
                    import kaleido
                    kaleido.get_chrome_sync()
                    print("Chrome installed successfully!")
                    # Retry after installation
                    return fig.to_image(format=format, engine='kaleido')
                except Exception as install_error:
                    raise RuntimeError(
                        f"Failed to install Chrome for Kaleido: {install_error}\n"
                        f"Original error: {e}\n"
                        f"Please install Chrome manually or contact support."
                    )
            else:
                # Re-raise if it's not a Chrome-related error
                raise
