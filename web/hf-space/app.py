"""Lightweight Hugging Face Space for camo-eval."""

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
    boundary_iou,
    camouflage_difficulty,
    dice,
    dists,
    e_measure,
    edge_density,
    feature_congestion,
    iou,
    lpips,
    mae,
    ms_ssim,
    precision,
    recall,
    s_measure,
    ssim,
    subband_entropy,
    target_background_similarity,
    weighted_f_measure,
)
from camo_eval import evaluate, to_markdown  # noqa: E402
from camo_eval.visualization import error_map, mask_overlay  # noqa: E402


METRIC_GROUPS = {
    "COD core": ["mae", "fw", "sm", "em", "f"],
    "PR diagnostics": ["precision", "recall"],
    "Region and boundary": ["iou", "dice", "boundary_iou"],
    "Mask similarity": ["ssim", "ms_ssim", "lpips_lite", "dists_lite"],
    "Clutter and difficulty": [
        "edge_density",
        "subband_entropy",
        "feature_congestion",
        "camouflage_difficulty",
    ],
    "Target-background similarity": [
        "tb_all",
        "tb_near",
    ],
}

DEFAULT_GROUPS = ["COD core", "PR diagnostics", "Region and boundary"]


def _demo_examples() -> list[list[str]]:
    return [
        [
            str(DEMO_ROOT / "images" / "sample1.png"),
            str(DEMO_ROOT / "pred" / "sample1.png"),
            str(DEMO_ROOT / "gt" / "sample1.png"),
            DEFAULT_GROUPS,
            "model",
            "rgb",
            "image-cod",
            "COD/SOD metric visualization demo / sample1",
        ],
        [
            str(DEMO_ROOT / "images" / "sample2.png"),
            str(DEMO_ROOT / "pred" / "sample2.png"),
            str(DEMO_ROOT / "gt" / "sample2.png"),
            DEFAULT_GROUPS,
            "model",
            "rgb",
            "image-cod",
            "COD/SOD metric visualization demo / sample2",
        ],
    ]


def _to_gray_array(image: Image.Image | None) -> np.ndarray:
    if image is None:
        raise gr.Error("Both prediction and ground-truth images are required.")
    return np.asarray(image.convert("L"))


def _compute_grouped_metrics(
    scene: np.ndarray | None, pred: np.ndarray, gt: np.ndarray, groups: list[str] | None
) -> dict[str, dict[str, float | dict[str, float]]]:
    selected = groups or DEFAULT_GROUPS
    metrics: dict[str, dict[str, float | dict[str, float]]] = {}

    if "COD core" in selected:
        metrics["COD core"] = {
            "MAE": mae(pred, gt),
            "Fw": weighted_f_measure(pred, gt),
            "Sm": s_measure(pred, gt),
            "Em": e_measure(pred, gt),
        }
    if "PR diagnostics" in selected:
        metrics["PR diagnostics"] = {
            "Precision": precision(pred, gt),
            "Recall": recall(pred, gt),
        }
    if "Region and boundary" in selected:
        metrics["Region and boundary"] = {
            "IoU": iou(pred, gt),
            "Dice": dice(pred, gt),
            "BoundaryIoU": boundary_iou(pred, gt),
        }
    if "Mask similarity" in selected:
        metrics["Mask similarity"] = {
            "SSIM": ssim(pred, gt),
            "MS_SSIM": ms_ssim(pred, gt),
            "LPIPS_lite": lpips(pred, gt),
            "DISTS_lite": dists(pred, gt),
        }
    if "Clutter and difficulty" in selected:
        # These are scene-clutter metrics; computing them on the binary GT mask
        # (when no scene is uploaded) produces meaningless numbers, so gate the
        # whole group on a scene being present.
        if scene is None:
            metrics["Clutter and difficulty"] = {
                "status": "Upload a scene image to compute scene-clutter metrics."
            }
        else:
            metrics["Clutter and difficulty"] = {
                "edge_density": edge_density(scene),
                "subband_entropy": subband_entropy(scene),
                "feature_congestion": feature_congestion(scene),
                "camouflage_difficulty": camouflage_difficulty(scene, gt),
            }
    if "Target-background similarity" in selected:
        if scene is None:
            metrics["Target-background similarity"] = {
                "status": "Upload a scene image to compute this group."
            }
        else:
            metrics["Target-background similarity"] = {
                "all_background": target_background_similarity(scene, gt, mode="all"),
                "near_background": target_background_similarity(scene, gt, mode="near"),
            }
    return metrics


def evaluate_demo(
    scene_image: Image.Image | None,
    pred_image: Image.Image | None,
    gt_image: Image.Image | None,
    metric_groups: list[str] | None,
    observer: str,
    channel: str,
    task: str,
    protocol: str,
) -> tuple[str, str, np.ndarray, np.ndarray]:
    scene = None if scene_image is None else _to_gray_array(scene_image)
    pred = _to_gray_array(pred_image)
    gt = _to_gray_array(gt_image)
    # Domain errors (mismatched sizes, empty/degenerate masks) raise ValueError
    # deep in camo-eval; surface them as a clean gr.Error instead of a raw
    # traceback.
    try:
        metrics = _compute_grouped_metrics(scene, pred, gt, metric_groups)
        overlay = mask_overlay(pred, gt)
        emap = error_map(pred, gt)
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc

    context = EvaluationContext(
        observer=observer,
        channel=channel,
        task=task,
        protocol=protocol or "ad hoc upload",
    )
    report = EvaluationReport(context=context, metrics=metrics)
    return (
        json.dumps(report.to_dict(), indent=2),
        report.to_markdown(),
        overlay,
        emap,
    )


def evaluate_demo_dataset() -> tuple[str, str]:
    results = evaluate(
        DEMO_ROOT / "pred",
        DEMO_ROOT / "gt",
        [
            "mae",
            "fw",
            "sm",
            "em",
            "f",
            "precision",
            "recall",
            "iou",
            "dice",
            "boundary_iou",
            "ssim",
            "ms_ssim",
            "lpips_lite",
            "dists_lite",
        ],
    )
    context = EvaluationContext(
        observer="model",
        channel="rgb",
        task="image-cod",
        protocol="COD/SOD metric visualization demo",
        notes="Synthetic repository-local 96x96 mask dataset",
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


with gr.Blocks(title="camo-eval Space") as demo:
    gr.Markdown("# camo-eval")
    gr.Markdown(
        "Upload a scene, prediction, and ground-truth mask, or run the bundled "
        "repository demo dataset. This Space only computes lightweight metrics "
        "that do not require large datasets or model weights."
    )

    with gr.Tab("Single Pair"):
        with gr.Row():
            scene_image = gr.Image(type="pil", label="Scene Image")
            pred_image = gr.Image(type="pil", label="Prediction")
            gt_image = gr.Image(type="pil", label="Ground Truth")

        metric_groups = gr.CheckboxGroup(
            choices=list(METRIC_GROUPS),
            value=DEFAULT_GROUPS,
            label="Metric Groups",
        )

        with gr.Row():
            observer = gr.Dropdown(
                choices=["model", "human", "operator", "hybrid"],
                value="model",
                label="Observer",
            )
            channel = gr.Dropdown(
                choices=[
                    "rgb",
                    "video",
                    "thermal",
                    "multispectral",
                    "multimodal",
                    "radar",
                    "custom",
                ],
                value="rgb",
                label="Channel",
            )
            task = gr.Dropdown(
                choices=[
                    "image-cod",
                    "video-cod",
                    "instance-cod",
                    "physical-adversarial",
                    "generation",
                    "human-search",
                    "signature-analysis",
                    "custom",
                ],
                value="image-cod",
                label="Task",
            )

        protocol = gr.Textbox(label="Protocol", value="interactive demo")
        run_button = gr.Button("Evaluate Pair")

        with gr.Row():
            json_output = gr.Code(label="JSON Report", language="json")
            markdown_output = gr.Textbox(label="Markdown Report", lines=18)
        with gr.Row():
            overlay_output = gr.Image(label="Mask Overlay", type="numpy")
            error_output = gr.Image(label="Error Map", type="numpy")

        gr.Examples(
            examples=_demo_examples(),
            inputs=[
                scene_image,
                pred_image,
                gt_image,
                metric_groups,
                observer,
                channel,
                task,
                protocol,
            ],
        )

        run_button.click(
            fn=evaluate_demo,
            inputs=[
                scene_image,
                pred_image,
                gt_image,
                metric_groups,
                observer,
                channel,
                task,
                protocol,
            ],
            outputs=[json_output, markdown_output, overlay_output, error_output],
        )

    with gr.Tab("Demo Dataset"):
        gr.Markdown(
            "Run the tiny repository-local demo dataset through the batch evaluator and package the result as a protocol-aware report."
        )
        dataset_button = gr.Button("Evaluate Demo Dataset")
        dataset_json = gr.Code(label="Dataset Report", language="json")
        dataset_markdown = gr.Textbox(label="Batch Markdown Table", lines=18)
        dataset_button.click(
            fn=evaluate_demo_dataset,
            inputs=[],
            outputs=[dataset_json, dataset_markdown],
        )


if __name__ == "__main__":
    # Hugging Face Spaces proxies to the container, so the app must bind 0.0.0.0;
    # binding loopback would make a deployed Space unreachable. Allow a local
    # override via GRADIO_SERVER_NAME (e.g. 127.0.0.1) when running privately.
    demo.launch(server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"))
