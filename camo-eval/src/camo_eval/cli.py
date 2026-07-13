"""Command-line interface for camo-eval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import (
    ResultsTable,
    camouflage_difficulty,
    edge_density,
    evaluate,
    feature_congestion,
    fid_lite,
    kid_lite,
    precision_recall_curve,
    subband_entropy,
    to_latex,
    to_markdown,
)
from .protocols import (
    EvaluationContext,
    EvaluationReport,
    build_protocol_manifest,
    load_protocol_manifest,
)
from .runner import _load_array, _metric_value
from .visualization import error_map, mask_overlay


def _emit_text(text: str, output_path: str | None) -> None:
    rendered = text + ("\n" if not text.endswith("\n") else "")
    if output_path:
        Path(output_path).write_text(rendered, encoding="utf-8")
    else:
        print(text)


def _results_to_json(results: ResultsTable) -> str:
    return json.dumps({"columns": results.columns, "rows": results.rows}, indent=2)


def _report_to_text(report: EvaluationReport, output_format: str) -> str:
    if output_format == "json":
        return report.to_json()
    if output_format == "markdown":
        return report.to_markdown()
    raise ValueError(f"Unsupported report format {output_format!r}")


def _mapping_to_markdown(mapping: dict[str, object]) -> str:
    lines = []
    for key, value in mapping.items():
        if value is None:
            continue
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines)


def _scores_to_text(scores: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(scores, indent=2)
    lines: list[str] = []
    for key, value in scores.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subvalue in value.items():
                lines.append(f"  {subkey}: {subvalue}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _available_metrics() -> dict[str, list[str]]:
    return {
        "detection": ["mae", "fw", "sm", "em", "f", "precision", "recall"],
        "instance": ["iou", "dice", "boundary_match_score"],
        "video": ["j", "boundary_f_lite", "jf_lite", "temporal"],
        "perceptual": ["ssim", "ms_ssim_lite", "lpips_lite", "dists_lite"],
        "generation": ["fid_lite", "kid_lite", "lpips_lite", "dists_lite"],
        "clutter": [
            "edge_density",
            "subband_entropy",
            "feature_congestion",
            "camouflage_difficulty",
        ],
        "signature": [
            "thermal_contrast",
            "signal_to_clutter_ratio",
            "spectral_angle_mapper",
        ],
    }


def _save_visualization_outputs(
    pred_path: str,
    gt_path: str,
    metrics: list[str],
    output_dir: str,
    threshold: float,
) -> dict[str, str]:
    try:
        import matplotlib.pyplot as plt
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Visualization requires Pillow and matplotlib. "
            "Install with `pip install camo-eval[full]`."
        ) from exc

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred = _load_array(Path(pred_path))
    gt = _load_array(Path(gt_path))

    scores: dict[str, float] = {}
    for metric in metrics:
        for name, value in _metric_value(metric, pred, gt).items():
            scores[name] = float(value)

    overlay_path = out_dir / "mask_overlay.png"
    error_path = out_dir / "error_map.png"
    curve_path = out_dir / "pr_curve.png"
    scores_path = out_dir / "scores.json"

    Image.fromarray(mask_overlay(pred, gt, threshold=threshold)).save(overlay_path)
    Image.fromarray(error_map(pred, gt, threshold=threshold)).save(error_path)

    curve = precision_recall_curve(pred, gt)
    fig, axis = plt.subplots(figsize=(5, 4), dpi=140)
    axis.plot(curve["recall"], curve["precision"], color="#1f6f8b", linewidth=2)
    axis.set(xlim=(0, 1), ylim=(0, 1.02), xlabel="Recall", ylabel="Precision")
    axis.set_title("Precision-Recall Curve")
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(curve_path)
    plt.close(fig)

    scores_path.write_text(json.dumps(scores, indent=2), encoding="utf-8")
    return {
        "mask_overlay": str(overlay_path.resolve()),
        "error_map": str(error_path.resolve()),
        "pr_curve": str(curve_path.resolve()),
        "scores": str(scores_path.resolve()),
    }


def _add_context_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--observer", required=True)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--notes")
    parser.add_argument("--dataset-version")
    parser.add_argument("--prediction-revision")
    parser.add_argument("--threshold-policy")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--environment")
    parser.add_argument("--uncertainty")


def _context_from_args(args: argparse.Namespace) -> EvaluationContext:
    return EvaluationContext(
        observer=args.observer,
        channel=args.channel,
        task=args.task,
        protocol=args.protocol,
        notes=args.notes,
        dataset_version=getattr(args, "dataset_version", None),
        prediction_revision=getattr(args, "prediction_revision", None),
        threshold_policy=getattr(args, "threshold_policy", None),
        seed=getattr(args, "seed", None),
        environment=getattr(args, "environment", None),
        uncertainty=getattr(args, "uncertainty", None),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="camo-eval", description="Protocol-aware camouflage evaluation preview"
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
        "protocol-template", help="Emit a protocol-aware report or manifest template"
    )
    _add_context_arguments(protocol_parser)
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
        help="Evaluate matching files and attach protocol/provenance metadata",
    )
    report_parser.add_argument("--pred-dir", required=True)
    report_parser.add_argument("--gt-dir", required=True)
    report_parser.add_argument("--metrics", nargs="+", required=True)
    _add_context_arguments(report_parser)
    report_parser.add_argument("--pred-source")
    report_parser.add_argument("--gt-source")
    report_parser.add_argument("--format", choices=("markdown", "json"), default="json")
    report_parser.add_argument("--output")

    manifest_parser = subparsers.add_parser(
        "evaluate-protocol", help="Run evaluation from a validated JSON manifest"
    )
    manifest_parser.add_argument("--manifest", required=True)
    manifest_parser.add_argument(
        "--root", help="Optional root for resolving relative prediction/GT paths"
    )
    manifest_parser.add_argument(
        "--format", choices=("markdown", "json"), default="json"
    )
    manifest_parser.add_argument("--output")

    visual_parser = subparsers.add_parser(
        "visualize", help="Create mask visualizations and a score JSON"
    )
    visual_parser.add_argument("--pred", required=True)
    visual_parser.add_argument("--gt", required=True)
    visual_parser.add_argument(
        "--metrics",
        nargs="+",
        default=[
            "mae",
            "fw",
            "sm",
            "em",
            "f",
            "precision",
            "recall",
            "iou",
            "dice",
            "boundary_match_score",
            "lpips_lite",
            "dists_lite",
        ],
    )
    visual_parser.add_argument("--threshold", type=float, default=0.5)
    visual_parser.add_argument("--output-dir", required=True)
    visual_parser.add_argument("--format", choices=("json", "text"), default="json")

    generation_parser = subparsers.add_parser(
        "generation-distance",
        help="Compute explicitly lightweight directory-level generation diagnostics",
    )
    generation_parser.add_argument("--real-dir", required=True)
    generation_parser.add_argument("--fake-dir", required=True)
    generation_parser.add_argument(
        "--metrics", nargs="+", default=["fid_lite", "kid_lite"]
    )
    generation_parser.add_argument("--format", choices=("json", "text"), default="json")
    generation_parser.add_argument("--output")

    diagnostics_parser = subparsers.add_parser(
        "image-diagnostics", help="Compute exploratory clutter diagnostics"
    )
    diagnostics_parser.add_argument("--image", required=True)
    diagnostics_parser.add_argument("--mask")
    diagnostics_parser.add_argument("--edge-threshold", type=float)
    diagnostics_parser.add_argument(
        "--format", choices=("json", "text"), default="json"
    )
    diagnostics_parser.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "evaluate":
        results = evaluate(args.pred_dir, args.gt_dir, args.metrics)
        if args.format == "markdown":
            output = to_markdown(results)
        elif args.format == "latex":
            output = to_latex(results)
        else:
            output = _results_to_json(results)
        _emit_text(output, args.output)
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
        context = _context_from_args(args)
        manifest_inputs = [args.pred_dir, args.gt_dir, args.metrics]
        if any(value is not None for value in manifest_inputs) and not all(
            value is not None for value in manifest_inputs
        ):
            parser.error(
                "protocol-template requires --pred-dir, --gt-dir, and --metrics together"
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
            output = (
                json.dumps(manifest, indent=2)
                if args.format == "json"
                else _mapping_to_markdown(manifest)
            )
        else:
            output = _report_to_text(
                EvaluationReport(context=context, metrics={}, artifacts={}), args.format
            )
        _emit_text(output, args.output)
        return 0

    if args.command == "evaluate-report":
        results = evaluate(args.pred_dir, args.gt_dir, args.metrics)
        artifacts = {
            "pred_dir": str(Path(args.pred_dir).resolve()),
            "gt_dir": str(Path(args.gt_dir).resolve()),
        }
        if args.pred_source:
            artifacts["pred_source"] = args.pred_source
        if args.gt_source:
            artifacts["gt_source"] = args.gt_source
        report = EvaluationReport(
            context=_context_from_args(args),
            metrics=results.rows[0] if results.rows else {},
            artifacts=artifacts,
        )
        _emit_text(_report_to_text(report, args.format), args.output)
        return 0

    if args.command == "evaluate-protocol":
        manifest = load_protocol_manifest(args.manifest)
        manifest_path = Path(args.manifest).resolve()
        root = Path(args.root).resolve() if args.root else manifest_path.parent
        pred_dir = root / str(manifest["pred_dir"])
        gt_dir = root / str(manifest["gt_dir"])
        results = evaluate(pred_dir, gt_dir, list(manifest["metrics"]))
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
            context=EvaluationContext.from_mapping(manifest),
            metrics=results.rows[0] if results.rows else {},
            artifacts=artifacts,
        )
        _emit_text(_report_to_text(report, args.format), args.output)
        return 0

    if args.command == "visualize":
        outputs = _save_visualization_outputs(
            pred_path=args.pred,
            gt_path=args.gt,
            metrics=list(args.metrics),
            output_dir=args.output_dir,
            threshold=args.threshold,
        )
        output = (
            json.dumps(outputs, indent=2)
            if args.format == "json"
            else _mapping_to_markdown(outputs)
        )
        _emit_text(output, None)
        return 0

    if args.command == "generation-distance":
        scores: dict[str, float] = {}
        for metric in args.metrics:
            key = metric.lower()
            if key == "fid_lite":
                scores["FID_lite"] = fid_lite(args.real_dir, args.fake_dir)
            elif key == "kid_lite":
                scores["KID_lite"] = kid_lite(args.real_dir, args.fake_dir)
            elif key in {"lpips_lite", "dists_lite"}:
                parser.error(f"{metric!r} is pairwise; use `evaluate` or `visualize`.")
            else:
                parser.error(f"Unsupported generation-distance metric {metric!r}.")
        _emit_text(_scores_to_text(scores, args.format), args.output)
        return 0

    if args.command == "image-diagnostics":
        image = _load_array(Path(args.image))
        scores: dict[str, object] = {
            "edge_density": edge_density(image, threshold=args.edge_threshold),
            "subband_entropy": subband_entropy(image),
            "feature_congestion": feature_congestion(image),
        }
        if args.mask:
            mask = _load_array(Path(args.mask))
            scores["camouflage_difficulty"] = camouflage_difficulty(image, mask)
        _emit_text(_scores_to_text(scores, args.format), args.output)
        return 0

    parser.error(f"Unknown command {args.command!r}")
    return 2
