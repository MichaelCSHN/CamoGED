"""Lightweight Hugging Face Space for camo-eval."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gradio as gr
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "camo-eval" / "src"))
DEMO_ROOT = ROOT / "camo-eval" / "demo_data" / "rgb_masks"

from camo_eval import (  # noqa: E402
    EvaluationContext,
    EvaluationReport,
    boundary_iou,
    dice,
    e_measure,
    iou,
    mae,
    ms_ssim,
    s_measure,
    ssim,
    weighted_f_measure,
)
from camo_eval import evaluate, to_markdown  # noqa: E402


def _demo_examples() -> list[list[str]]:
    return [
        [
            str(DEMO_ROOT / "pred" / "sample1.pgm"),
            str(DEMO_ROOT / "gt" / "sample1.pgm"),
            "model",
            "rgb",
            "image-cod",
            "repository demo bundle / sample1",
        ],
        [
            str(DEMO_ROOT / "pred" / "sample2.pgm"),
            str(DEMO_ROOT / "gt" / "sample2.pgm"),
            "model",
            "rgb",
            "image-cod",
            "repository demo bundle / sample2",
        ],
    ]


def _to_gray_array(image: Image.Image | None) -> np.ndarray:
    if image is None:
        raise gr.Error("Both prediction and ground-truth images are required.")
    return np.asarray(image.convert("L"))


def evaluate_demo(
    pred_image: Image.Image | None,
    gt_image: Image.Image | None,
    observer: str,
    channel: str,
    task: str,
    protocol: str,
) -> tuple[str, str]:
    pred = _to_gray_array(pred_image)
    gt = _to_gray_array(gt_image)

    metrics = {
        "MAE": mae(pred, gt),
        "Fw": weighted_f_measure(pred, gt),
        "Sm": s_measure(pred, gt),
        "Em": e_measure(pred, gt),
        "IoU": iou(pred, gt),
        "Dice": dice(pred, gt),
        "BoundaryIoU": boundary_iou(pred, gt),
        "SSIM": ssim(pred, gt),
        "MS_SSIM": ms_ssim(pred, gt),
    }

    context = EvaluationContext(
        observer=observer,
        channel=channel,
        task=task,
        protocol=protocol or "ad hoc upload",
    )
    report = EvaluationReport(context=context, metrics=metrics)
    return json.dumps(report.to_dict(), indent=2), report.to_markdown()


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
            "iou",
            "dice",
            "boundary_iou",
            "ssim",
            "ms_ssim",
        ],
    )
    context = EvaluationContext(
        observer="model",
        channel="rgb",
        task="image-cod",
        protocol="repository demo bundle",
        notes="Synthetic repository-local demo dataset",
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
        "Upload a prediction and a ground-truth mask, or run the bundled repository demo dataset."
    )

    with gr.Tab("Single Pair"):
        with gr.Row():
            pred_image = gr.Image(type="pil", label="Prediction")
            gt_image = gr.Image(type="pil", label="Ground Truth")

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

        gr.Examples(
            examples=_demo_examples(),
            inputs=[pred_image, gt_image, observer, channel, task, protocol],
        )

        run_button.click(
            fn=evaluate_demo,
            inputs=[pred_image, gt_image, observer, channel, task, protocol],
            outputs=[json_output, markdown_output],
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
    demo.launch(server_name="127.0.0.1")
