# Portfolio Notes

## Project Story

This project is designed to showcase a full analytics workflow instead of just a dashboard. The value is not only in calculating metrics, but also in translating raw business performance into a report that leadership teams can quickly understand.

## What Makes It Portfolio-Quality

- It solves a realistic business reporting problem.
- It combines data cleaning, KPI design, visualization, and AI reporting.
- It uses modular Python files so the logic is easy to explain during interviews.
- It includes a usable Streamlit interface instead of a notebook-only workflow.
- It saves generated outputs, which makes the project feel product-like.

## Talking Points for Interviews

- Explain how the selected date range is compared with an equally long previous period.
- Walk through how KPIs are separated into reusable metric functions.
- Show how the analysis payload is packaged into a prompt for executive reporting.
- Mention the fallback summary mode for cases when an API key is not available.
- Highlight how the app bridges analysis and decision support.

## Good Demo Flow

1. Start with the sample CSV.
2. Select a date range that creates a meaningful comparison.
3. Show KPI movement and category changes.
4. Generate the executive report.
5. Open a saved report from `outputs/generated_reports/`.
