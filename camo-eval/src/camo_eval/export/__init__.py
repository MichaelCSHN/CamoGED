"""Tabular export helpers."""

from __future__ import annotations

from ..results import ResultsTable


def _format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def to_markdown(results: ResultsTable) -> str:
    """Render a :class:`ResultsTable` as a markdown table."""

    header = "| " + " | ".join(results.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(results.columns)) + " |"
    rows = []
    for row in results.rows:
        rows.append(
            "| "
            + " | ".join(
                _format_value(row.get(column, "")) for column in results.columns
            )
            + " |"
        )
    return "\n".join([header, separator, *rows])


def to_latex(results: ResultsTable) -> str:
    """Render a :class:`ResultsTable` as a minimal LaTeX tabular."""

    cols = "l" * len(results.columns)
    header = " & ".join(results.columns) + r" \\"
    body = [
        " & ".join(_format_value(row.get(column, "")) for column in results.columns)
        + r" \\"
        for row in results.rows
    ]
    return "\n".join(
        [
            rf"\begin{{tabular}}{{{cols}}}",
            r"\hline",
            header,
            r"\hline",
            *body,
            r"\hline",
            r"\end{tabular}",
        ]
    )
