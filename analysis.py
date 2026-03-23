from __future__ import annotations

from datetime import timedelta

import pandas as pd

from src.metrics import calculate_kpis, compare_kpis, format_kpi_table


def filter_data_by_date_range(
    dataframe: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    """Keep only the rows that fall inside the selected reporting window."""
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    # This mask keeps rows on or after the start date and on or before the end date.
    mask = (dataframe["date"] >= start_ts) & (dataframe["date"] <= end_ts)
    return dataframe.loc[mask].copy().reset_index(drop=True)


def create_previous_period(
    dataframe: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp
) -> tuple[pd.DataFrame, dict[str, pd.Timestamp]]:
    """Create a previous period with the same number of days automatically."""
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    # Add one day because both the start and end dates are included in the selection.
    number_of_days = (end_ts - start_ts).days + 1
    previous_end_date = start_ts - timedelta(days=1)
    previous_start_date = previous_end_date - timedelta(days=number_of_days - 1)

    previous_period_df = filter_data_by_date_range(
        dataframe,
        previous_start_date,
        previous_end_date,
    )

    return previous_period_df, {
        "start_date": previous_start_date,
        "end_date": previous_end_date,
    }


def summarize_period_overview(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create a daily business summary for charts and quick checks."""
    daily_summary = (
        dataframe.groupby("date", as_index=False)
        .agg(
            Revenue=("revenue", "sum"),
            Profit=("profit", "sum"),
            Orders=("order_id", "nunique"),
        )
        .sort_values("date")
    )
    return daily_summary.reset_index(drop=True)


def summarize_revenue_by_category(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Summarize current-period revenue by category."""
    category_summary = (
        dataframe.groupby("category", as_index=False)
        .agg(
            **{
                "Category": ("category", "first"),
                "Revenue": ("revenue", "sum"),
                "Orders": ("order_id", "nunique"),
                "Profit": ("profit", "sum"),
            }
        )
        .drop(columns=["category"])
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )
    return category_summary


def compare_category_revenue(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> pd.DataFrame:
    """Compare category revenue between the selected period and previous period."""
    current_summary = (
        current_df.groupby("category", as_index=False)
        .agg(
            **{
                "Category": ("category", "first"),
                "Current Revenue": ("revenue", "sum"),
                "Current Orders": ("order_id", "nunique"),
                "Current Profit": ("profit", "sum"),
            }
        )
        .drop(columns=["category"])
    )

    previous_summary = (
        previous_df.groupby("category", as_index=False)
        .agg(
            **{
                "Category": ("category", "first"),
                "Previous Revenue": ("revenue", "sum"),
                "Previous Orders": ("order_id", "nunique"),
                "Previous Profit": ("profit", "sum"),
            }
        )
        .drop(columns=["category"])
    )

    comparison = current_summary.merge(previous_summary, on="Category", how="outer").fillna(0)
    comparison["Revenue Change"] = comparison["Current Revenue"] - comparison["Previous Revenue"]
    comparison["Profit Change"] = comparison["Current Profit"] - comparison["Previous Profit"]
    comparison["Revenue Change %"] = comparison.apply(
        lambda row: None
        if row["Previous Revenue"] == 0
        else (row["Current Revenue"] - row["Previous Revenue"]) / row["Previous Revenue"],
        axis=1,
    )

    return comparison.sort_values("Current Revenue", ascending=False).reset_index(drop=True)


def _build_product_revenue_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create a simple revenue table at the product level."""
    product_table = (
        dataframe.groupby("product_name", as_index=False)
        .agg(
            **{
                "Product": ("product_name", "first"),
                "Revenue": ("revenue", "sum"),
                "Units Sold": ("quantity", "sum"),
                "Orders": ("order_id", "nunique"),
            }
        )
        .drop(columns=["product_name"])
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )
    return product_table


def find_top_and_bottom_products(dataframe: pd.DataFrame, limit: int = 10) -> dict[str, pd.DataFrame]:
    """Return the top and bottom products by revenue."""
    product_table = _build_product_revenue_table(dataframe)

    top_products = product_table.head(limit).reset_index(drop=True)
    bottom_products = product_table.sort_values("Revenue", ascending=True).head(limit).reset_index(drop=True)

    return {
        "top_products": top_products,
        "bottom_products": bottom_products,
    }


def product_performance_compare(
    current_df: pd.DataFrame, previous_df: pd.DataFrame, limit: int = 10
) -> pd.DataFrame:
    """Compare product revenue and return the top products for the selected period."""
    current_summary = (
        current_df.groupby("product_name", as_index=False)
        .agg(
            **{
                "Product": ("product_name", "first"),
                "Current Revenue": ("revenue", "sum"),
                "Current Units": ("quantity", "sum"),
            }
        )
        .drop(columns=["product_name"])
    )

    previous_summary = (
        previous_df.groupby("product_name", as_index=False)
        .agg(
            **{
                "Product": ("product_name", "first"),
                "Previous Revenue": ("revenue", "sum"),
                "Previous Units": ("quantity", "sum"),
            }
        )
        .drop(columns=["product_name"])
    )

    comparison = current_summary.merge(previous_summary, on="Product", how="outer").fillna(0)
    comparison["Revenue Change"] = comparison["Current Revenue"] - comparison["Previous Revenue"]
    comparison["Revenue Change %"] = comparison.apply(
        lambda row: None
        if row["Previous Revenue"] == 0
        else (row["Current Revenue"] - row["Previous Revenue"]) / row["Previous Revenue"],
        axis=1,
    )

    return comparison.sort_values("Current Revenue", ascending=False).head(limit).reset_index(drop=True)


def detect_revenue_anomalies(category_comparison_df: pd.DataFrame, threshold: float = 0.30) -> pd.DataFrame:
    """Flag categories where revenue changed by more than 30 percent."""
    anomaly_table = category_comparison_df.copy()

    # Ignore rows where percent change cannot be calculated because there was no previous revenue.
    anomaly_table = anomaly_table[anomaly_table["Revenue Change %"].notna()]

    # Keep only large swings in either direction.
    anomaly_table = anomaly_table[anomaly_table["Revenue Change %"].abs() > threshold]

    if anomaly_table.empty:
        return pd.DataFrame(
            columns=["Business Area", "Current Revenue", "Previous Revenue", "Revenue Change", "Revenue Change %"]
        )

    anomaly_table = anomaly_table.rename(columns={"Category": "Business Area"})
    anomaly_table = anomaly_table[
        ["Business Area", "Current Revenue", "Previous Revenue", "Revenue Change", "Revenue Change %"]
    ]
    return anomaly_table.sort_values("Revenue Change %").reset_index(drop=True)


def category_performance_compare(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> pd.DataFrame:
    """Compatibility wrapper used by the Streamlit app."""
    return compare_category_revenue(current_df, previous_df)


def build_analysis_outputs(
    dataframe: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> dict[str, pd.DataFrame | dict]:
    """Run the main business analysis workflow and return simple outputs."""
    current_df = filter_data_by_date_range(dataframe, start_date, end_date)
    previous_df, previous_period = create_previous_period(dataframe, start_date, end_date)
    category_summary = summarize_revenue_by_category(current_df)
    category_comparison = compare_category_revenue(current_df, previous_df)
    product_rankings = find_top_and_bottom_products(current_df, limit=10)
    anomalies = detect_revenue_anomalies(category_comparison, threshold=0.30)

    return {
        "current_period_data": current_df,
        "previous_period_data": previous_df,
        "previous_period_dates": previous_period,
        "daily_summary": summarize_period_overview(current_df),
        "category_summary": category_summary,
        "category_comparison": category_comparison,
        "top_10_products": product_rankings["top_products"],
        "bottom_10_products": product_rankings["bottom_products"],
        "revenue_anomalies": anomalies,
    }


def build_analysis_payload(
    current_df: pd.DataFrame,
    previous_df: pd.DataFrame,
    current_label: str,
    previous_label: str,
) -> dict:
    """Package analysis outputs into a dictionary for report generation."""
    current_kpis = calculate_kpis(current_df)
    previous_kpis = calculate_kpis(previous_df)
    kpi_comparison = format_kpi_table(compare_kpis(current_kpis, previous_kpis))
    category_summary = summarize_revenue_by_category(current_df)
    category_comparison = compare_category_revenue(current_df, previous_df)
    product_rankings = find_top_and_bottom_products(current_df, limit=10)
    anomalies = detect_revenue_anomalies(category_comparison, threshold=0.30)

    return {
        "current_period": current_label,
        "previous_period": previous_label,
        "current_kpis": current_kpis,
        "previous_kpis": previous_kpis,
        "kpi_comparison": kpi_comparison.to_dict(orient="records"),
        "daily_summary": summarize_period_overview(current_df).round(2).to_dict(orient="records"),
        "category_summary": category_summary.round(2).to_dict(orient="records"),
        "category_comparison": category_comparison.round(2).to_dict(orient="records"),
        "top_10_products": product_rankings["top_products"].round(2).to_dict(orient="records"),
        "bottom_10_products": product_rankings["bottom_products"].round(2).to_dict(orient="records"),
        "anomalies": anomalies.round(2).to_dict(orient="records"),
    }
