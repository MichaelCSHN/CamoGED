"""Command-line interface for camo-eval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import (
    ResultsTable,
    evaluate,
    to_latex,
    to_markdown,
)
from .protocols import (
    EvaluationContext,
    EvaluationReport,
    build_protocol_manifest,
    load_protocol_manifest,
)


def _results_to_json(results: ResultsTable) -> str:
    return json.dumps({"columns": results.columns, "rows": results.rows}, indent=2)


def _report_to_text(report: EvaluationReport, output_format: str) -> str:
    if output_format == "json":
        return report.to_json()
    if output_format == "markdown":
        return report.to_markdown()
    raise ValueError(f"Unsupported report format {output_format!r}")


def _emit_text(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(
            text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8"
        )
    else:
        print(text)


def _available_metrics() -> dict[str, list[str]]:
    return {
        "detection": ["mae", "fw", "sm", "em", "f"],
        "instance": ["iou", "dice", "boundary_iou"],
        "video": ["j", "boundary_f", "jf", "temporal"],
        "perceptual": ["ssim", "ms_ssim"],
        "signature": [
            "thermal_contrast",
            "signal_to_clutter_ratio",
            "spectral_angle_mapper",
        ],
    }


def _manifest_to_text(manifest: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(manifest, indent=2)
    lines = [
        f"- observer: `{manifest['observer']}`",
        f"- channel: `{manifest['channel']}`",
        f"- task: `{manifest['task']}`",
        f"- protocol: `{manifest['protocol']}`",
        f"- pred_dir: `{manifest['pred_dir']}`",
        f"- gt_dir: `{manifest['gt_dir']}`",
        f"- metrics: `{', '.join(manifest['metrics'])}`",
    ]
    if manifest.get("name"):
        lines.append(f"- name: `{manifest['name']}`")
    if manifest.get("notes"):
        lines.append(f"- notes: {manifest['notes']}")
    if manifest.get("pred_source"):
        lines.append(f"- pred_source: {manifest['pred_source']}")
    if manifest.get("gt_source"):
        lines.append(f"- gt_source: {manifest['gt_source']}")
    return "\n".join(lines)


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
    evaluate_parser.add_argument("--output")

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
    protocol_parser.add_argument("--name")
    protocol_parser.add_argument("--pred-dir")
    protocol_parser.add_argument("--gt-dir")
    protocol_parser.add_argument("--metrics", nargs="+")
    protocol_parser.add_argument("--pred-source")
    protocol_parser.add_argument("--gt-source")
    protocol_parser.add_argument(
        "--format", choices=("markdown", "json"), default="json"
    )
    protocol_parser.add_argument("--output")

    report_parser = subparsers.add_parser(
        "evaluate-report",
        help="Run batch evaluation and wrap the result in a protocol-aware report",
    )
    report_parser.add_argument("--pred-dir", required=True)
    report_parser.add_argument("--gt-dir", required=True)
    report_parser.add_argument("--metrics", nargs="+", required=True)
    report_parser.add_argument("--observer", required=True)
    report_parser.add_argument("--channel", required=True)
    report_parser.add_argument("--task", required=True)
    report_parser.add_argument("--protocol", required=True)
    report_parser.add_argument("--notes")
    report_parser.add_argument("--pred-source")
    report_parser.add_argument("--gt-source")
    report_parser.add_argument("--format", choices=("markdown", "json"), default="json")
    report_parser.add_argument("--output")

    manifest_parser = subparsers.add_parser(
        "evaluate-protocol",
        help="Run evaluation from a protocol manifest that defines context, paths, and metrics",
    )
    manifest_parser.add_argument("--manifest", required=True)
    manifest_parser.add_argument(
        "--root",
        help="Optional root directory used to resolve relative pred/gt directories from the manifest",
    )
    manifest_parser.add_argument(
        "--format", choices=("markdown", "json"), default="json"
    )
    manifest_parser.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "evaluate":
        results = evaluate(args.pred_dir, args.gt_dir, args.metrics)
        if args.format == "markdown":
            _emit_text(to_markdown(results), args.output)
        elif args.format == "latex":
            _emit_text(to_latex(results), args.output)
        else:
            _emit_text(_results_to_json(results), args.output)
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
        manifest_inputs = [args.pred_dir, args.gt_dir, args.metrics]
        if any(value is not None for value in manifest_inputs) and not all(
            value is not None for value in manifest_inputs
        ):
            parser.error(
                "protocol-template requires --pred-dir, --gt-dir, and --metrics together "
                "when generating an executable manifest"
            )
        if all(value is not None for value in manifest_inputs):
            manifest = build_protocol_manifest(
                context=context,
                pred_dir=args.pred_dir,
                gt_dir=args.gt_dir,
                metrics=list(args.metrics),
                name=args.name,
                pred_source=args.pred_source,
                gt_source=args.gt_source,
            )
            _emit_text(_manifest_to_text(manifest, args.format), args.output)
            return 0
        report = EvaluationReport(context=context, metrics={}, artifacts={})
        _emit_text(_report_to_text(report, args.format), args.output)
        return 0

    if args.command == "evaluate-report":
        results = evaluate(args.pred_dir, args.gt_dir, args.metrics)
        context = EvaluationContext(
            observer=args.observer,
            channel=args.channel,
            task=args.task,
            protocol=args.protocol,
            notes=args.notes,
        )
        metrics = results.rows[0] if results.rows else {}
        artifacts = {
            "pred_dir": str(Path(args.pred_dir).resolve()),
            "gt_dir": str(Path(args.gt_dir).resolve()),
        }
        if args.pred_source:
            artifacts["pred_source"] = args.pred_source
        if args.gt_source:
            artifacts["gt_source"] = args.gt_source
        report = EvaluationReport(context=context, metrics=metrics, artifacts=artifacts)
        _emit_text(_report_to_text(report, args.format), args.output)
        return 0

    if args.command == "evaluate-protocol":
        manifest = load_protocol_manifest(args.manifest)
        manifest_path = Path(args.manifest).resolve()
        root = Path(args.root).resolve() if args.root else manifest_path.parent

        pred_dir = root / str(manifest["pred_dir"])
        gt_dir = root / str(manifest["gt_dir"])
        results = evaluate(pred_dir, gt_dir, list(manifest["metrics"]))
        context = EvaluationContext(
            observer=str(manifest["observer"]),
            channel=str(manifest["channel"]),
            task=str(manifest["task"]),
            protocol=str(manifest["protocol"]),
            notes=manifest.get("notes"),
        )
        artifacts = {
            "manifest": str(manifest_path),
            "pred_dir": str(pred_dir.resolve()),
            "gt_dir": str(gt_dir.resolve()),
            "bundle_name": str(manifest.get("name", "")),
        }
        for key in ("pred_source", "gt_source"):
            if manifest.get(key):
                artifacts[key] = str(manifest[key])
        report = EvaluationReport(
            context=context,
            metrics=results.rows[0] if results.rows else {},
            artifacts=artifacts,
        )
        _emit_text(_report_to_text(report, args.format), args.output)
        return 0

    parser.error(f"Unknown command {args.command!r}")
    return 2
