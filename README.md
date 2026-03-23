# AI Business Report Generator

AI Business Report Generator is a portfolio project that combines business analytics, interactive reporting, and AI-generated executive communication in one end-to-end application. Built with Streamlit, pandas, Plotly, and the OpenAI API, the app helps turn raw sales data into a decision-ready business report.

This project is designed to showcase more than dashboard building. It demonstrates how an analyst can move from messy operational data to KPI analysis, period-over-period comparisons, visualization, and leadership-facing insight generation in a single workflow.

## Project Summary

The app allows a user to upload a CSV sales dataset, filter a selected reporting window, compare that period against the previous period, calculate core business KPIs, review charts and summary tables, and generate a concise executive-style markdown report.

The result is a lightweight business intelligence tool that connects analysis with communication, which is often the missing step in analytics portfolios.

## Business Problem

Business teams often spend significant time manually pulling together recurring performance updates. That process usually involves:

- cleaning transaction-level data
- calculating KPIs by hand or in spreadsheets
- comparing current performance against a previous period
- identifying major changes across categories or products
- translating findings into a stakeholder-friendly summary

This workflow is repetitive, time-consuming, and inconsistent. It also makes it easy to miss important changes or rely on subjective explanations.

This project solves that problem by creating a repeatable reporting pipeline that:

- standardizes KPI calculation
- automates period-over-period comparison
- highlights meaningful changes and anomalies
- turns structured analysis into an executive-ready report

## Features

- Upload a CSV sales dataset directly in the Streamlit app
- Validate required columns and clean the data automatically
- Filter results by selected date range
- Compare the selected period against an automatically generated previous period
- Calculate key business KPIs:
  Revenue, Orders, Average Order Value, Profit, and Profit Margin
- Summarize revenue by category
- Identify top and bottom products by revenue
- Flag anomalies where revenue changes by more than 30%
- Visualize revenue trends and rankings with Plotly charts
- Generate a concise executive report using the OpenAI API
- Return a fallback non-AI summary if the API key is missing or the API call fails
- Save generated reports as markdown files for reuse and sharing

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly
- OpenAI API
- python-dotenv

## Folder Structure

```text
ai-report-generator/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   └── this.csv
├── src/
│   ├── load_data.py
│   ├── metrics.py
│   ├── analysis.py
│   ├── charts.py
│   ├── report_prompt.py
│   └── llm_report.py
├── outputs/
│   └── generated_reports/
└── docs/
    └── portfolio_notes.md
```

## How to Run Locally

1. Clone or download the project.
2. Open a terminal in the `ai-report-generator` folder.
3. Create and activate a virtual environment.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Optional: enable AI report generation by copying the environment template and adding your OpenAI API key:

```bash
cp .env.example .env
```

6. Run the app:

```bash
streamlit run app.py
```

7. Open the local Streamlit URL shown in the terminal.

## Example Use Case

Imagine a small consumer brand reviewing January sales performance.

An analyst uploads the transaction dataset, selects a reporting window such as January 15 to January 31, and instantly compares it with the previous period of equal length. The app calculates key KPIs, shows which categories gained or lost revenue, highlights top-performing and weak-performing products, and flags any major swings that deserve attention.

Instead of manually assembling findings into a presentation or Slack update, the analyst can generate a concise executive report that summarizes the most important business movement in a professional format.

## What This Project Demonstrates for Analyst Roles

This project is especially relevant for business analyst, product analyst, data analyst, and analytics engineer portfolios because it shows:

- ability to translate a business reporting problem into a technical solution
- strong understanding of KPI design and period-over-period analysis
- practical experience cleaning and validating raw data
- ability to turn transaction-level data into stakeholder-friendly summaries
- dashboard and reporting skills using Streamlit and Plotly
- thoughtful use of AI for business communication, not just automation for its own sake
- modular, readable Python code that is easy to explain in interviews
- end-to-end product thinking from data input to final output

## Why This Works as a Portfolio Project

Many portfolio projects stop at charts. This one goes further by showing how analysis supports decision-making. It demonstrates both technical execution and business communication, which is especially valuable in analyst roles where insight delivery matters just as much as the analysis itself.
