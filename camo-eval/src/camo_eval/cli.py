"""Command-line interface for camo-eval."""

from __future__ import annotations

import argparse
import json

from . import (
    ResultsTable,
    evaluate,
    to_latex,
    to_markdown,
)
from .protocols import EvaluationContext, EvaluationReport


def _results_to_json(results: ResultsTable) -> str:
    return json.dumps({"columns": results.columns, "rows": results.rows}, indent=2)


def _available_metrics() -> dict[str, list[str]]:
    return {
        "detection": ["mae", "fw", "sm", "em", "f"],
        "instance": ["iou", "dice", "boundary_iou"],
        "video": ["j", "boundary_f", "jf", "temporal"],
        "perceptual": ["ssim", "ms_ssim"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="camo-eval", description="Camouflage evaluation toolkit CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Run batch evaluation over matching files"
    )
    evaluate_parser.add_argument("--pred-dir", required=True)
    evaluate_parser.add_argument("--gt-dir", required=True)
    evaluate_parser.add_argument("--metrics", nargs="+", required=True)
    evaluate_parser.add_argument(
        "--format", choices=("markdown", "latex", "json"), default="markdown"
    )

    list_parser = subparsers.add_parser(
        "list-metrics", help="List built-in metric groups"
    )
    list_parser.add_argument("--format", choices=("text", "json"), default="text")

    protocol_parser = subparsers.add_parser(
        "protocol-template", help="Emit a protocol-aware evaluation report template"
    )
    protocol_parser.add_argument("--observer", required=True)
    protocol_parser.add_argument("--channel", required=True)
    protocol_parser.add_argument("--task", required=True)
    protocol_parser.add_argument("--protocol", required=True)
    protocol_parser.add_argument("--notes")
    protocol_parser.add_argument(
        "--format", choices=("markdown", "json"), default="json"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "evaluate":
        results = evaluate(args.pred_dir, args.gt_dir, args.metrics)
        if args.format == "markdown":
            print(to_markdown(results))
        elif args.format == "latex":
            print(to_latex(results))
        else:
            print(_results_to_json(results))
        return 0

    if args.command == "list-metrics":
        metrics = _available_metrics()
        if args.format == "json":
            print(json.dumps(metrics, indent=2))
        else:
            for family, names in metrics.items():
                print(f"{family}: {', '.join(names)}")
        return 0

    if args.command == "protocol-template":
        context = EvaluationContext(
            observer=args.observer,
            channel=args.channel,
            task=args.task,
            protocol=args.protocol,
            notes=args.notes,
        )
        report = EvaluationReport(context=context, metrics={}, artifacts={})
        if args.format == "markdown":
            print(report.to_markdown())
        else:
            print(report.to_json())
        return 0

    parser.error(f"Unknown command {args.command!r}")
    return 2
