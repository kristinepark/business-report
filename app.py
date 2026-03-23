from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import (
    build_analysis_payload,
    category_performance_compare,
    detect_revenue_anomalies,
    find_top_and_bottom_products,
    product_performance_compare,
    summarize_period_overview,
    summarize_revenue_by_category,
)
from src.charts import (
    create_category_revenue_chart,
    create_revenue_trend_chart,
    create_top_products_chart,
)
from src.llm_report import generate_llm_report, save_report
from src.load_data import (
    apply_dimension_filters,
    filter_by_date,
    get_date_bounds,
    get_previous_period,
    load_sales_data,
)
from src.metrics import calculate_kpis, compare_kpis, format_kpi_table
from src.report_prompt import build_executive_report_prompt


st.set_page_config(
    page_title="AI Business Report Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)


PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_DATA_PATH = PROJECT_ROOT / "data" / "this.csv"
REPORTS_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "generated_reports"


def apply_custom_css() -> None:
    """Add a polished SaaS dashboard style to the app."""
    st.markdown(
        """
        <style>
            :root {
                --page-bg: #f6fbff;
                --surface: rgba(255, 255, 255, 0.94);
                --surface-solid: #ffffff;
                --text: #102033;
                --muted: #5e7187;
                --border: rgba(148, 163, 184, 0.20);
                --primary: #2563eb;
                --primary-soft: rgba(37, 99, 235, 0.10);
                --secondary: #14b8a6;
                --warning: #f59e0b;
                --shadow: 0 18px 45px rgba(16, 32, 51, 0.08);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 30%),
                    radial-gradient(circle at top right, rgba(20, 184, 166, 0.13), transparent 28%),
                    linear-gradient(180deg, #f9fcff 0%, #eef6ff 100%);
                color: var(--text);
            }

            .block-container {
                padding-top: 1.6rem;
                padding-bottom: 2rem;
            }

            .hero-shell {
                background:
                    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(237, 247, 255, 0.92)),
                    linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(20, 184, 166, 0.05));
                border: 1px solid var(--border);
                border-radius: 30px;
                padding: 1.6rem 1.7rem;
                box-shadow: var(--shadow);
                margin-bottom: 1.1rem;
                overflow: hidden;
                position: relative;
            }

            .hero-shell::after {
                content: "";
                position: absolute;
                top: -40px;
                right: -30px;
                width: 220px;
                height: 220px;
                background: radial-gradient(circle, rgba(37, 99, 235, 0.14), transparent 65%);
                pointer-events: none;
            }

            .hero-badge {
                display: inline-block;
                background: var(--primary-soft);
                color: var(--primary);
                border: 1px solid rgba(37, 99, 235, 0.08);
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                border-radius: 999px;
                padding: 0.42rem 0.72rem;
                margin-bottom: 0.8rem;
            }

            .hero-title {
                font-size: 2.5rem;
                line-height: 1.02;
                font-weight: 800;
                letter-spacing: -0.03em;
                color: var(--text);
                margin: 0;
                max-width: 40rem;
            }

            .hero-copy {
                color: var(--muted);
                font-size: 1.03rem;
                line-height: 1.6;
                max-width: 44rem;
                margin: 0.8rem 0 0 0;
            }

            .hero-stats {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 1.2rem;
            }

            .hero-stat {
                background: rgba(255, 255, 255, 0.8);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.9rem 1rem;
            }

            .hero-stat-label {
                color: var(--muted);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 700;
            }

            .hero-stat-value {
                color: var(--text);
                font-size: 1.1rem;
                font-weight: 800;
                margin-top: 0.3rem;
            }

            .kpi-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1rem 1.05rem;
                box-shadow: var(--shadow);
                min-height: 132px;
            }

            .kpi-label {
                color: var(--muted);
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                margin-bottom: 0.45rem;
            }

            .kpi-value {
                color: var(--text);
                font-size: 1.95rem;
                line-height: 1.08;
                font-weight: 800;
                letter-spacing: -0.02em;
            }

            .kpi-delta {
                margin-top: 0.45rem;
                font-size: 0.95rem;
                font-weight: 700;
            }

            .delta-up { color: #0f766e; }
            .delta-down { color: #dc2626; }
            .delta-flat { color: var(--muted); }

            .panel-card {
                background: var(--surface-solid);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1.15rem 1.2rem;
                box-shadow: var(--shadow);
            }

            .panel-heading {
                margin: 0 0 0.35rem 0;
                color: var(--text);
                font-size: 1.15rem;
                font-weight: 800;
            }

            .panel-copy {
                margin: 0;
                color: var(--muted);
                line-height: 1.55;
            }

            .report-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(249,252,255,0.96));
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1.25rem 1.35rem;
                box-shadow: var(--shadow);
            }

            .report-card h2, .report-card h3 {
                color: var(--text);
            }

            .report-card p, .report-card li, .report-card blockquote {
                color: #304256;
                line-height: 1.65;
            }

            .summary-strip {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                box-shadow: var(--shadow);
                margin: 1rem 0 1.15rem 0;
                color: var(--muted);
            }

            div[data-baseweb="tab-list"] {
                gap: 0.65rem;
                background: rgba(255, 255, 255, 0.72);
                padding: 0.4rem;
                border-radius: 18px;
                border: 1px solid var(--border);
                margin: 1rem 0 1rem 0;
            }

            button[data-baseweb="tab"] {
                border-radius: 14px;
                padding: 0.58rem 1rem;
                font-weight: 700;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #fbfdff 0%, #edf5ff 100%);
                border-right: 1px solid rgba(148, 163, 184, 0.18);
            }

            @media (max-width: 900px) {
                .hero-stats {
                    grid-template-columns: 1fr;
                }
                .hero-title {
                    font-size: 2rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_metric_value(metric_name: str, value: float) -> str:
    """Format KPI values for the dashboard."""
    if metric_name == "Profit Margin":
        return f"{value:.1%}"
    if metric_name == "Orders":
        return f"{int(value):,}"
    return f"${value:,.2f}"


def format_delta_text(delta_pct: float | None) -> tuple[str, str]:
    """Create a friendly delta label for KPI cards."""
    if delta_pct is None or pd.isna(delta_pct):
        return "No prior period", "delta-flat"
    if delta_pct > 0:
        return f"Up {delta_pct:.2f}% vs prior", "delta-up"
    if delta_pct < 0:
        return f"Down {abs(delta_pct):.2f}% vs prior", "delta-down"
    return "Flat vs prior", "delta-flat"


def render_kpi_card(metric_name: str, metric_row: pd.Series) -> None:
    """Render one KPI card with custom HTML styling."""
    delta_text, delta_class = format_delta_text(metric_row["change_pct"])
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{metric_name}</div>
            <div class="kpi-value">{format_metric_value(metric_name, metric_row["current"])}</div>
            <div class="kpi-delta {delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_header(title: str, description: str) -> None:
    """Show a reusable card-style intro above each content area."""
    st.markdown(
        f"""
        <div class="panel-card">
            <h3 class="panel-heading">{title}</h3>
            <p class="panel-copy">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_selected_dataset(uploaded_file, use_sample: bool) -> pd.DataFrame:
    """Load either the uploaded dataset or the bundled sample dataset."""
    if uploaded_file is None and not use_sample:
        raise ValueError("Upload a CSV file or turn on the sample dataset option.")
    file_source = uploaded_file if uploaded_file is not None else SAMPLE_DATA_PATH
    return load_sales_data(file_source)


def main() -> None:
    apply_custom_css()

    if "report_text" not in st.session_state:
        st.session_state.report_text = ""
        st.session_state.report_source = ""
        st.session_state.report_file_name = ""

    with st.sidebar:
        st.header("Workspace")
        uploaded_file = st.file_uploader("Upload sales CSV", type=["csv"])
        use_sample = st.toggle("Use sample coffee dataset", value=uploaded_file is None)
        st.caption(
            "The sample dataset is bundled with the project. Uploaded files are cleaned automatically "
            "to handle common naming differences in business exports."
        )

    try:
        raw_df = load_selected_dataset(uploaded_file, use_sample)
    except Exception as error:
        st.error(
            "The dataset could not be loaded. Please check the CSV columns and try again. "
            f"Details: {error}"
        )
        st.stop()

    min_date, max_date = get_date_bounds(raw_df)

    with st.sidebar:
        st.header("Filters")
        selected_dates = st.date_input(
            "Date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )

        if not isinstance(selected_dates, tuple) or len(selected_dates) != 2:
            st.warning("Please select both a start date and an end date.")
            st.stop()

        selected_regions = st.multiselect("Region", sorted(raw_df["region"].dropna().unique()))
        selected_channels = st.multiselect("Channel", sorted(raw_df["channel"].dropna().unique()))
        selected_categories = st.multiselect("Category", sorted(raw_df["category"].dropna().unique()))
        anomaly_threshold_pct = st.slider(
            "Anomaly threshold (%)",
            min_value=10,
            max_value=60,
            value=30,
            step=5,
        )

    filtered_base_df = apply_dimension_filters(
        raw_df,
        regions=selected_regions,
        channels=selected_channels,
        categories=selected_categories,
    )

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])
    current_df = filter_by_date(filtered_base_df, start_date, end_date)
    previous_df, previous_period = get_previous_period(filtered_base_df, start_date, end_date)

    if current_df.empty:
        st.warning("No rows match the current filters. Try widening the date range or clearing a filter.")
        st.stop()

    current_label = f"{start_date.date()} to {end_date.date()}"
    previous_label = f"{previous_period[0].date()} to {previous_period[1].date()}"

    current_kpis = calculate_kpis(current_df)
    previous_kpis = calculate_kpis(previous_df)
    kpi_table = format_kpi_table(compare_kpis(current_kpis, previous_kpis))
    daily_summary = summarize_period_overview(current_df)
    category_summary = summarize_revenue_by_category(current_df).round(2)
    category_comparison = category_performance_compare(current_df, previous_df).round(2)
    top_products = product_performance_compare(current_df, previous_df, limit=10).round(2)
    product_rankings = find_top_and_bottom_products(current_df, limit=10)
    anomaly_table = detect_revenue_anomalies(
        category_comparison,
        threshold=anomaly_threshold_pct / 100,
    ).round(2)
    analysis_payload = build_analysis_payload(current_df, previous_df, current_label, previous_label)

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-badge">Modern SaaS Analytics Dashboard</div>
            <h1 class="hero-title">Transform sales data into executive-ready business reporting.</h1>
            <p class="hero-copy">
                Filter performance by period, region, category, and channel, explore trends with interactive
                charts, and generate a polished executive summary from the analysis in one workflow.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-label">Current period</div>
                    <div class="hero-stat-value">{current_label}</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Previous period</div>
                    <div class="hero-stat-value">{previous_label}</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Rows in scope</div>
                    <div class="hero-stat-value">{len(current_df):,}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="summary-strip">
            <strong>Dashboard focus:</strong> revenue trend, category mix, top products, and anomaly flags
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Threshold:</strong> {anomaly_threshold_pct}% revenue change
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_names = ["Revenue", "Orders", "Average Order Value", "Profit Margin"]
    kpi_columns = st.columns(4, gap="medium")
    for column, metric_name in zip(kpi_columns, kpi_names):
        metric_row = kpi_table[kpi_table["metric"] == metric_name].iloc[0]
        with column:
            label = "AOV" if metric_name == "Average Order Value" else metric_name
            render_kpi_card(label, metric_row)

    overview_tab, deep_dive_tab, ai_report_tab = st.tabs(
        ["Overview", "Performance Deep Dive", "AI Executive Report"]
    )

    with overview_tab:
        render_panel_header(
            "Executive snapshot",
            "Use this view for a clean, high-level read on trend direction, category contribution, and the products leading revenue right now.",
        )
        st.write("")

        overview_col_1, overview_col_2 = st.columns(2, gap="large")
        with overview_col_1:
            st.plotly_chart(create_revenue_trend_chart(daily_summary), use_container_width=True)
        with overview_col_2:
            st.plotly_chart(create_category_revenue_chart(category_summary), use_container_width=True)

        st.plotly_chart(create_top_products_chart(top_products, limit=10), use_container_width=True)

        table_col_1, table_col_2 = st.columns(2, gap="large")
        with table_col_1:
            st.markdown("#### KPI comparison")
            st.dataframe(kpi_table, use_container_width=True, hide_index=True)
        with table_col_2:
            st.markdown("#### Revenue by category")
            st.dataframe(category_summary, use_container_width=True, hide_index=True)

    with deep_dive_tab:
        render_panel_header(
            "Performance diagnostics",
            "Dive into period-over-period movement, anomaly signals, and the products driving the strongest and weakest results.",
        )
        st.write("")

        deep_col_1, deep_col_2 = st.columns(2, gap="large")
        with deep_col_1:
            st.markdown("#### Category comparison")
            st.dataframe(category_comparison, use_container_width=True, hide_index=True)
        with deep_col_2:
            st.markdown(f"#### Revenue anomalies above {anomaly_threshold_pct}%")
            if anomaly_table.empty:
                st.info("No category-level anomalies crossed the selected threshold.")
            else:
                st.dataframe(anomaly_table, use_container_width=True, hide_index=True)

        product_col_1, product_col_2 = st.columns(2, gap="large")
        with product_col_1:
            st.markdown("#### Top 10 products")
            st.dataframe(product_rankings["top_products"].round(2), use_container_width=True, hide_index=True)
        with product_col_2:
            st.markdown("#### Bottom 10 products")
            st.dataframe(product_rankings["bottom_products"].round(2), use_container_width=True, hide_index=True)

    with ai_report_tab:
        render_panel_header(
            "AI executive report",
            "Generate a concise leadership-ready summary from the current analysis. The report is displayed in a polished card and can be downloaded as markdown.",
        )
        st.write("")

        button_col, status_col = st.columns([1, 2], gap="large")
        with button_col:
            if st.button("Generate Executive Summary", type="primary", use_container_width=True):
                with st.spinner("Generating executive summary..."):
                    prompt = build_executive_report_prompt(analysis_payload)
                    report_text, report_source = generate_llm_report(prompt, analysis_payload)
                    saved_path = save_report(report_text, REPORTS_OUTPUT_PATH)

                st.session_state.report_text = report_text
                st.session_state.report_source = report_source
                st.session_state.report_file_name = saved_path.name

        with status_col:
            if st.session_state.report_text:
                st.success(f"Latest report generated with: {st.session_state.report_source}")
            else:
                st.info("Generate a summary after reviewing the dashboard filters and comparison views.")

        if st.session_state.report_text:
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.report_text)
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")
            st.download_button(
                "Download report",
                data=st.session_state.report_text,
                file_name=st.session_state.report_file_name or "executive_report.md",
                mime="text/markdown",
            )


if __name__ == "__main__":
    main()
