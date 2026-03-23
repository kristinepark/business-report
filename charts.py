from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _apply_clean_chart_style(figure: go.Figure) -> go.Figure:
    """Apply one shared style so all charts look polished and consistent."""
    figure.update_layout(
        template="plotly_white",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"family": "Arial", "size": 13},
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        legend_title_text="",
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="#E5E7EB")
    return figure


def create_revenue_trend_chart(revenue_df: pd.DataFrame) -> go.Figure:
    """Create a simple line chart that shows revenue over time."""
    date_column = "date"
    revenue_column = "Revenue" if "Revenue" in revenue_df.columns else "revenue"

    # Sort by date so the line always moves in the correct order.
    chart_data = revenue_df.sort_values(date_column).copy()

    figure = px.line(
        chart_data,
        x=date_column,
        y=revenue_column,
        markers=True,
        title="Revenue Trend Over Time",
        color_discrete_sequence=["#1D4ED8"],
    )

    figure.update_traces(line={"width": 3}, marker={"size": 7})
    figure.update_layout(xaxis_title="Date", yaxis_title="Revenue")
    return _apply_clean_chart_style(figure)


def create_category_revenue_chart(category_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing revenue by category."""
    category_column = "Category" if "Category" in category_df.columns else "category"

    if "Revenue" in category_df.columns:
        revenue_column = "Revenue"
        chart_title = "Revenue by Category"
    else:
        revenue_column = "Current Revenue" if "Current Revenue" in category_df.columns else "current_revenue"
        chart_title = "Current Period Revenue by Category"

    # Sort so the highest-revenue categories are easiest to compare.
    chart_data = category_df.sort_values(revenue_column, ascending=False).copy()

    figure = px.bar(
        chart_data,
        x=category_column,
        y=revenue_column,
        title=chart_title,
        color_discrete_sequence=["#0F766E"],
        text_auto=".2s",
    )

    figure.update_layout(xaxis_title="Category", yaxis_title="Revenue")
    figure.update_traces(hovertemplate="%{x}<br>Revenue: %{y:$,.2f}<extra></extra>")
    return _apply_clean_chart_style(figure)


def create_top_products_chart(product_df: pd.DataFrame, limit: int = 10) -> go.Figure:
    """Create a horizontal bar chart for the top products by revenue."""
    product_column = "Product" if "Product" in product_df.columns else "product_name"

    if "Revenue" in product_df.columns:
        revenue_column = "Revenue"
    else:
        revenue_column = "Current Revenue" if "Current Revenue" in product_df.columns else "current_revenue"

    # Keep only the top products, then reverse the order for a clean horizontal ranking chart.
    chart_data = (
        product_df.sort_values(revenue_column, ascending=False)
        .head(limit)
        .sort_values(revenue_column, ascending=True)
        .copy()
    )

    figure = px.bar(
        chart_data,
        x=revenue_column,
        y=product_column,
        orientation="h",
        title="Top 10 Products by Revenue",
        color_discrete_sequence=["#B45309"],
        text_auto=".2s",
    )

    figure.update_layout(xaxis_title="Revenue", yaxis_title="Product")
    figure.update_traces(hovertemplate="%{y}<br>Revenue: %{x:$,.2f}<extra></extra>")
    return _apply_clean_chart_style(figure)


def create_daily_revenue_chart(current_daily_df: pd.DataFrame) -> go.Figure:
    """Compatibility wrapper used by the Streamlit app."""
    return create_revenue_trend_chart(current_daily_df)


def create_category_comparison_chart(category_df: pd.DataFrame) -> go.Figure:
    """Compatibility wrapper used by the Streamlit app."""
    return create_category_revenue_chart(category_df)
