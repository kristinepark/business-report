from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


def get_openai_api_key() -> str | None:
    """Load environment variables and return the OpenAI API key if it exists."""
    # This reads values from a local .env file if the user created one.
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")


def generate_fallback_report(analysis_payload: dict, message: str | None = None) -> str:
    """Create a simple markdown summary when AI generation is unavailable."""
    current_kpis = analysis_payload.get("current_kpis", {})
    previous_kpis = analysis_payload.get("previous_kpis", {})
    category_comparison = analysis_payload.get("category_comparison", [])
    top_products = analysis_payload.get("top_10_products", [])
    anomalies = analysis_payload.get("anomalies", [])

    top_category = category_comparison[0]["Category"] if category_comparison else "N/A"
    top_product = top_products[0]["Product"] if top_products else "N/A"

    note = ""
    if message:
        note = f"> Note: {message}\n\n"

    # The fallback is still structured like an executive report so the app stays useful.
    return f"""
{note}## Overview
The selected period ({analysis_payload.get("current_period", "Selected Period")}) generated ${current_kpis.get("Revenue", 0):,.2f} in revenue from {current_kpis.get("Orders", 0):,} orders. Profit for the period was ${current_kpis.get("Profit", 0):,.2f}, with a profit margin of {current_kpis.get("Profit Margin", 0):.1%}.

## Key Changes
- Revenue: ${current_kpis.get("Revenue", 0):,.2f} vs ${previous_kpis.get("Revenue", 0):,.2f} in the previous period
- Orders: {current_kpis.get("Orders", 0):,} vs {previous_kpis.get("Orders", 0):,}
- Average Order Value: ${current_kpis.get("Average Order Value", 0):,.2f}
- Highest current-period category by revenue: {top_category}
- Highest current-period product by revenue: {top_product}

## Risks
- Review any categories or products that lost revenue compared with the previous period.
- Large movements should be investigated before drawing conclusions about performance direction.

## Opportunities
- Build on the strongest category and product results from the selected period.
- Use the category and product ranking tables to identify where growth is already visible.

## Recommended Actions
- Review the period-over-period KPI table for the biggest shifts.
- Investigate major category changes and anomaly flags in the dashboard.
- Re-run the report with an OpenAI API key for a richer narrative summary.
""".strip()


def generate_llm_report(prompt: str, analysis_payload: dict) -> tuple[str, str]:
    """Send the prompt to OpenAI and return markdown text, or fall back safely."""
    api_key = get_openai_api_key()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # If the API key is missing, return a readable local summary instead of failing.
    if not api_key:
        fallback_message = "OPENAI_API_KEY is missing, so a local summary was used instead."
        return generate_fallback_report(analysis_payload, message=fallback_message), "fallback"

    try:
        # Import here so the project can still run in fallback mode even if the package is unavailable.
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Send the prepared prompt to the model and return the markdown response text.
        response = client.responses.create(
            model=model,
            input=prompt,
        )
        return response.output_text.strip(), model
    except Exception as error:
        fallback_message = f"OpenAI report generation failed ({error}). A local summary was used instead."
        return generate_fallback_report(analysis_payload, message=fallback_message), "fallback"


def save_report(report_text: str, output_dir: str | Path) -> Path:
    """Save a generated report as a timestamped markdown file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_path / f"business_report_{timestamp}.md"
    file_path.write_text(report_text, encoding="utf-8")
    return file_path
