from __future__ import annotations

import pandas as pd


def calculate_total_revenue(dataframe: pd.DataFrame) -> float:
    """Add up all revenue in the dataframe."""
    return float(dataframe["revenue"].sum())


def calculate_total_orders(dataframe: pd.DataFrame) -> int:
    """Count unique orders in the dataframe."""
    return int(dataframe["order_id"].nunique())


def calculate_average_order_value(dataframe: pd.DataFrame) -> float:
    """Calculate average order value using revenue divided by orders."""
    total_revenue = calculate_total_revenue(dataframe)
    total_orders = calculate_total_orders(dataframe)
    return total_revenue / total_orders if total_orders else 0.0


def calculate_total_profit(dataframe: pd.DataFrame) -> float:
    """Add up profit across all rows."""
    return float(dataframe["profit"].sum())


def calculate_profit_margin(dataframe: pd.DataFrame) -> float:
    """Calculate profit margin as profit divided by revenue."""
    total_revenue = calculate_total_revenue(dataframe)
    total_profit = calculate_total_profit(dataframe)
    return total_profit / total_revenue if total_revenue else 0.0


def calculate_total_customers(dataframe: pd.DataFrame) -> int:
    """Count unique customers for the selected period."""
    return int(dataframe["customer_id"].nunique())


def calculate_units_sold(dataframe: pd.DataFrame) -> float:
    """Add up all units sold."""
    return float(dataframe["quantity"].sum())


def calculate_percent_change(current_value: float, previous_value: float) -> float | None:
    """Return percent change when the previous value is available."""
    if pd.isna(previous_value) or previous_value == 0:
        return None
    return (current_value - previous_value) / previous_value


def calculate_kpis(dataframe: pd.DataFrame) -> dict[str, float]:
    """Collect the main KPIs in one easy-to-use dictionary."""
    revenue = calculate_total_revenue(dataframe)
    orders = calculate_total_orders(dataframe)
    avg_order_value = calculate_average_order_value(dataframe)
    profit = calculate_total_profit(dataframe)
    profit_margin = calculate_profit_margin(dataframe)

    return {
        "Revenue": revenue,
        "Orders": orders,
        "Average Order Value": avg_order_value,
        "Profit": profit,
        "Profit Margin": profit_margin,
        "Customers": calculate_total_customers(dataframe),
        "Units Sold": calculate_units_sold(dataframe),
    }


def compare_metric(current_value: float, previous_value: float) -> dict[str, float | None]:
    """Compare one metric between the current period and previous period."""
    absolute_change = current_value - previous_value
    percent_change = calculate_percent_change(current_value, previous_value)

    return {
        "current_value": current_value,
        "previous_value": previous_value,
        "absolute_change": absolute_change,
        "percent_change": percent_change,
    }


def compare_kpis(current_kpis: dict[str, float], previous_kpis: dict[str, float]) -> pd.DataFrame:
    """Compare each KPI and return a table that is easy to display."""
    rows = []

    for metric_name, current_value in current_kpis.items():
        previous_value = previous_kpis.get(metric_name, 0.0)
        comparison = compare_metric(current_value, previous_value)

        rows.append(
            {
                "metric": metric_name,
                "current": comparison["current_value"],
                "previous": comparison["previous_value"],
                "change": comparison["absolute_change"],
                "change_pct": comparison["percent_change"],
            }
        )

    return pd.DataFrame(rows)


def format_kpi_table(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a friendly KPI table for the UI and report prompt."""
    table = comparison_df.copy()
    table["change_pct"] = table["change_pct"].apply(
        lambda value: None if value is None or pd.isna(value) else round(value * 100, 2)
    )
    table["current"] = table["current"].round(2)
    table["previous"] = table["previous"].round(2)
    table["change"] = table["change"].round(2)
    return table
