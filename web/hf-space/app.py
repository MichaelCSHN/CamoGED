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


with gr.Blocks(title="camo-eval Space") as demo:
    gr.Markdown("# camo-eval")
    gr.Markdown(
        "Upload a prediction and a ground-truth mask to compute core camouflage metrics."
    )

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
    run_button = gr.Button("Evaluate")

    with gr.Row():
        json_output = gr.Code(label="JSON Report", language="json")
        markdown_output = gr.Textbox(label="Markdown Report", lines=18)

    run_button.click(
        fn=evaluate_demo,
        inputs=[pred_image, gt_image, observer, channel, task, protocol],
        outputs=[json_output, markdown_output],
    )


if __name__ == "__main__":
    demo.launch()
