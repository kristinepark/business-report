from __future__ import annotations

import json


def build_executive_report_prompt(analysis_payload: dict) -> str:
    """Turn structured analysis results into a clear prompt for the LLM."""
    serialized_payload = json.dumps(analysis_payload, indent=2, default=str)

    return f"""
You are a senior business analyst writing a concise executive report for business leaders.

Your writing style should be:
- Professional
- Clear
- Business-oriented
- Concise
- Grounded only in the provided data

Write the report using exactly these section headings:
1. Overview
2. Key Changes
3. Risks
4. Opportunities
5. Recommended Actions

Requirements:
- Use only the information supported by the analysis results below.
- Do not make up causes, reasons, or explanations that are not directly supported by the data.
- If the data shows a change but not the cause, describe the change without guessing why it happened.
- Highlight the most important KPI movement, category shifts, product performance, and anomalies.
- If the previous period has limited or no data, clearly state that period-over-period conclusions are limited.
- Keep the report easy to scan with short paragraphs and bullet points when useful.
- Mention key numbers where they improve clarity.
- Focus on what an executive audience would care about most.

Structured analysis results:
{serialized_payload}
""".strip()
