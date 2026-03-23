from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import BinaryIO

import pandas as pd


REQUIRED_COLUMNS = [
    "date",
    "order_id",
    "customer_id",
    "region",
    "channel",
    "category",
    "product_name",
    "unit_price",
    "quantity",
    "discount",
    "revenue",
    "cost",
]

NUMERIC_COLUMNS = ["unit_price", "quantity", "discount", "revenue", "cost"]

COLUMN_ALIASES = {
    "sales": "revenue",
    "sale_amount": "revenue",
    "sales_amount": "revenue",
    "total_sales": "revenue",
    "product": "product_name",
    "productname": "product_name",
    "product_name_": "product_name",
    "orderid": "order_id",
    "customerid": "customer_id",
    "unitprice": "unit_price",
}


def normalize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Standardize uploaded column names so common CSV variations still work."""
    cleaned = dataframe.copy()

    normalized_columns = []
    for column in cleaned.columns:
        normalized_name = str(column).strip().lower().replace(" ", "_")
        normalized_name = COLUMN_ALIASES.get(normalized_name, normalized_name)
        normalized_columns.append(normalized_name)

    cleaned.columns = normalized_columns
    return cleaned


def validate_required_columns(dataframe: pd.DataFrame) -> None:
    """Raise a clear error when the CSV schema is missing required fields."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_list}")


def clean_numeric_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric fields safely and replace missing values with zero."""
    cleaned = dataframe.copy()

    for column in NUMERIC_COLUMNS:
        # Convert text values like "25" into numbers. Invalid values become NaN first.
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

        # Fill missing or invalid numeric values with zero so KPI calculations stay stable.
        cleaned[column] = cleaned[column].fillna(0)

    return cleaned


def load_sales_data(file_source: str | Path | BinaryIO) -> pd.DataFrame:
    """Load a CSV file, validate the schema, and return a cleaned dataframe."""
    # Read the CSV file. utf-8-sig helps when files include a hidden Excel-style BOM.
    dataframe = pd.read_csv(file_source, encoding="utf-8-sig")

    # Normalize uploaded column names to make the app friendlier to real CSV files.
    dataframe = normalize_column_names(dataframe)

    # Make sure the dataset includes every field the app needs.
    validate_required_columns(dataframe)

    # Convert the date column to datetime so filtering and comparisons work correctly.
    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce")
    if dataframe["date"].isna().any():
        raise ValueError("The date column contains invalid or missing values.")

    # Clean numeric columns before calculating derived metrics.
    dataframe = clean_numeric_columns(dataframe)

    # Create helper columns used later in the dashboard analysis.
    dataframe["profit"] = dataframe["revenue"] - dataframe["cost"]
    revenue_base = dataframe["revenue"].replace(0, pd.NA)
    gross_sales = (dataframe["unit_price"] * dataframe["quantity"]).replace(0, pd.NA)
    dataframe["profit_margin"] = dataframe["profit"] / revenue_base
    dataframe["discount_rate"] = dataframe["discount"] / gross_sales

    # Return a clean, date-sorted dataframe for consistent downstream analysis.
    return dataframe.sort_values("date").reset_index(drop=True)


def get_date_bounds(dataframe: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return the min and max dates in the dataset."""
    return dataframe["date"].min(), dataframe["date"].max()


def filter_by_date(
    dataframe: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    """Keep rows inside the selected date range."""
    mask = (dataframe["date"] >= pd.Timestamp(start_date)) & (
        dataframe["date"] <= pd.Timestamp(end_date)
    )
    return dataframe.loc[mask].copy()


def get_previous_period(
    dataframe: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp
) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp]]:
    """Build a previous period with the same number of days."""
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    selected_days = (end_ts - start_ts).days + 1
    previous_end = start_ts - timedelta(days=1)
    previous_start = previous_end - timedelta(days=selected_days - 1)
    previous_dataframe = filter_by_date(dataframe, previous_start, previous_end)
    return previous_dataframe, (previous_start, previous_end)


def apply_dimension_filters(
    dataframe: pd.DataFrame,
    regions: list[str] | None = None,
    channels: list[str] | None = None,
    categories: list[str] | None = None,
) -> pd.DataFrame:
    """Apply optional business filters before period analysis."""
    filtered = dataframe.copy()

    if regions:
        filtered = filtered[filtered["region"].isin(regions)]
    if channels:
        filtered = filtered[filtered["channel"].isin(channels)]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]

    return filtered.reset_index(drop=True)
