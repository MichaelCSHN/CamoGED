"""Lightweight Gradio surface for the camo-eval research preview."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import gradio as gr
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "camo-eval" / "src"))
DEMO_ROOT = ROOT / "camo-eval" / "demo_data" / "cod_sota_masks"

from camo_eval import (  # noqa: E402
    EvaluationContext,
    EvaluationReport,
    boundary_match_score,
    dice,
    dists_lite,
    e_measure,
    evaluate,
    iou,
    lpips_lite,
    mae,
    ms_ssim_lite,
    precision,
    recall,
    s_measure,
    ssim,
    to_markdown,
    weighted_f_measure,
)
from camo_eval.visualization import error_map, mask_overlay  # noqa: E402

METRIC_GROUPS = {
    "Validated COD core": ["mae", "fw", "sm", "em", "f", "precision", "recall"],
    "Validated region and SSIM": ["iou", "dice", "ssim"],
    "Experimental lite diagnostics": [
        "boundary_match_score",
        "ms_ssim_lite",
        "lpips_lite",
        "dists_lite",
    ],
}
DEFAULT_GROUPS = ["Validated COD core", "Validated region and SSIM"]


def _examples() -> list[list[str]]:
    return [
        [
            str(DEMO_ROOT / "images" / f"sample{index}.png"),
            str(DEMO_ROOT / "pred" / f"sample{index}.png"),
            str(DEMO_ROOT / "gt" / f"sample{index}.png"),
            DEFAULT_GROUPS,
            "model",
            "rgb",
            "image-cod",
            f"Synthetic repository fixture / sample{index}",
        ]
        for index in (1, 2)
    ]


def _gray(image: Image.Image | None) -> np.ndarray:
    if image is None:
        raise gr.Error("Prediction and ground-truth images are required.")
    return np.asarray(image.convert("L"))


def _grouped_metrics(
    pred: np.ndarray, gt: np.ndarray, groups: list[str] | None
) -> dict[str, dict[str, float | dict[str, float]]]:
    selected = groups or DEFAULT_GROUPS
    metrics: dict[str, dict[str, float | dict[str, float]]] = {}
    if "Validated COD core" in selected:
        metrics["Validated COD core"] = {
            "MAE": mae(pred, gt),
            "Fw": weighted_f_measure(pred, gt),
            "Sm": s_measure(pred, gt),
            "Em": e_measure(pred, gt),
            "Precision": precision(pred, gt),
            "Recall": recall(pred, gt),
        }
    if "Validated region and SSIM" in selected:
        metrics["Validated region and SSIM"] = {
            "IoU": iou(pred, gt),
            "Dice": dice(pred, gt),
            "SSIM": ssim(pred, gt),
        }
    if "Experimental lite diagnostics" in selected:
        metrics["Experimental lite diagnostics"] = {
            "BoundaryMatch_experimental": boundary_match_score(pred, gt),
            "MS_SSIM_lite": ms_ssim_lite(pred, gt),
            "LPIPS_lite": lpips_lite(pred, gt),
            "DISTS_lite": dists_lite(pred, gt),
        }
    return metrics


def evaluate_pair(
    scene_image: Image.Image | None,
    pred_image: Image.Image | None,
    gt_image: Image.Image | None,
    metric_groups: list[str] | None,
    observer: str,
    channel: str,
    task: str,
    protocol: str,
) -> tuple[str, str, np.ndarray, np.ndarray]:
    del scene_image  # Scene uploads are intentionally not evaluated by this mask-only Space.
    pred = _gray(pred_image)
    gt = _gray(gt_image)
    try:
        metrics = _grouped_metrics(pred, gt, metric_groups)
        overlay = mask_overlay(pred, gt)
        errors = error_map(pred, gt)
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc

    context = EvaluationContext(
        observer=observer,
        channel=channel,
        task=task,
        protocol=protocol or "ad hoc upload",
        notes=(
            "The Space does not retain uploads. Experimental lite metrics are not "
            "standard Boundary IoU, MS-SSIM, LPIPS, or DISTS."
        ),
    )
    report = EvaluationReport(context=context, metrics=metrics)
    return report.to_json(), report.to_markdown(), overlay, errors


def evaluate_demo_dataset() -> tuple[str, str]:
    metrics = ["mae", "fw", "sm", "em", "f", "precision", "recall", "iou", "dice", "ssim"]
    results = evaluate(DEMO_ROOT / "pred", DEMO_ROOT / "gt", metrics)
    context = EvaluationContext(
        observer="model",
        channel="rgb",
        task="image-cod",
        protocol="synthetic repository fixture",
        notes="No external dataset is redistributed by this demo bundle.",
    )
    report = EvaluationReport(
        context=context,
        metrics=results.rows[0],
        artifacts={
            "pred_dir": str((DEMO_ROOT / "pred").resolve()),
            "gt_dir": str((DEMO_ROOT / "gt").resolve()),
        },
    )
    return json.dumps(report.to_dict(), indent=2), to_markdown(results)


with gr.Blocks(title="camo-eval research preview") as demo:
    gr.Markdown("# camo-eval research preview")
    gr.Markdown(
        "This Space evaluates prediction/ground-truth masks. Standard names are shown only "
        "for validated implementations; approximations are explicitly labelled experimental "
        "or `_lite`. Uploaded files are processed for the session and are not a hosted model input."
    )

    with gr.Tab("Single pair"):
        with gr.Row():
            scene_image = gr.Image(type="pil", label="Optional scene (display only)")
            pred_image = gr.Image(type="pil", label="Prediction")
            gt_image = gr.Image(type="pil", label="Ground truth")
        metric_groups = gr.CheckboxGroup(
            choices=list(METRIC_GROUPS), value=DEFAULT_GROUPS, label="Metric groups"
        )
        with gr.Row():
            observer = gr.Dropdown(
                choices=["model", "human", "operator", "hybrid"], value="model", label="Observer"
            )
            channel = gr.Dropdown(
                choices=["rgb", "video", "thermal", "multispectral", "multimodal", "radar", "custom"],
                value="rgb",
                label="Channel",
            )
            task = gr.Dropdown(
                choices=["image-cod", "video-cod", "instance-cod", "generation", "custom"],
                value="image-cod",
                label="Task",
            )
        protocol = gr.Textbox(label="Protocol", value="interactive synthetic demonstration")
        run_button = gr.Button("Evaluate pair")
        with gr.Row():
            json_output = gr.Code(label="JSON report", language="json")
            markdown_output = gr.Textbox(label="Markdown report", lines=18)
        with gr.Row():
            overlay_output = gr.Image(label="Mask overlay", type="numpy")
            error_output = gr.Image(label="TP/FP/FN error map", type="numpy")
        gr.Examples(
            examples=_examples(),
            inputs=[scene_image, pred_image, gt_image, metric_groups, observer, channel, task, protocol],
        )
        run_button.click(
            fn=evaluate_pair,
            inputs=[scene_image, pred_image, gt_image, metric_groups, observer, channel, task, protocol],
            outputs=[json_output, markdown_output, overlay_output, error_output],
        )

    with gr.Tab("Synthetic fixture batch"):
        gr.Markdown("Runs the repository-local synthetic mask fixture; no third-party dataset is bundled.")
        dataset_button = gr.Button("Evaluate synthetic fixture")
        dataset_json = gr.Code(label="Dataset report", language="json")
        dataset_markdown = gr.Textbox(label="Batch table", lines=18)
        dataset_button.click(
            fn=evaluate_demo_dataset,
            inputs=[],
            outputs=[dataset_json, dataset_markdown],
        )


if __name__ == "__main__":
    demo.launch(server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"))
