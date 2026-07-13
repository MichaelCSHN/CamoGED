#!/usr/bin/env python3
"""Check book-wide navigation and review-derived editorial contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CHAPTERS = BOOK / "chapters"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    quarto = yaml.safe_load(read(BOOK / "_quarto.yml"))

    chapter_files: list[str] = []
    for item in quarto["book"]["chapters"]:
        if isinstance(item, dict):
            chapter_files.extend(item.get("chapters", []))

    if len(chapter_files) != 21:
        errors.append(f"expected 21 numbered chapters, found {len(chapter_files)}")

    index = read(BOOK / "index.qmd")
    for token in (
        "## 全书导航与依赖关系",
        "flowchart LR",
        "| 21 | 前沿与责任边界",
        "机制、历史与文化",
        "第四篇：评价",
    ):
        if token not in index:
            errors.append(f"book/index.qmd missing {token!r}")

    ch1 = read(CHAPTERS / "01-essence-and-the-game.qmd")
    for token in (
        "隐真与示假",
        "concealing the real",
        "presenting the false",
        "\\not\\Rightarrow",
        "设计手段不等于功能效果",
    ):
        if token not in ch1:
            errors.append(f"chapter 1 missing {token!r}")

    for rel in chapter_files:
        path = BOOK / rel
        text = read(path)
        if text.count("## 本章与全书映射") != 1:
            errors.append(f"{rel}: expected exactly one mapping card")
            continue
        for token in ("**本章定位**", "**前后依赖**", "**证据与风险边界**"):
            if token not in text:
                errors.append(f"{rel}: mapping card missing {token}")
        if "## 延伸阅读" in text and text.index("## 本章与全书映射") > text.index("## 延伸阅读"):
            errors.append(f"{rel}: mapping card must precede further reading")

    appendix = read(CHAPTERS / "appendix-resources.qmd")
    for token in (
        "dataset_hashes:",
        "prediction_hashes:",
        "environment_lock:",
        "container_image_digest:",
        "pollution_audit:",
        "query_budget:",
        "concealing the real / presenting the false",
        "docs/EVALUATION_MANIFEST_EXTENSION_V1.md",
    ):
        if token not in appendix:
            errors.append(f"appendix-resources.qmd missing {token!r}")

    expected_appendix = "chapters/appendix-research-agenda.qmd"
    if expected_appendix not in quarto["book"].get("appendices", []):
        errors.append("_quarto.yml missing research-agenda appendix")
    agenda_path = BOOK / expected_appendix
    if not agenda_path.exists():
        errors.append("research-agenda appendix file missing")
    else:
        agenda = read(agenda_path)
        for token in (
            "SQ1",
            "SQ2",
            "SQ3",
            "SQ4",
            "SQ5",
            "SQ6",
            "人类观察者实验伦理与预注册模板",
            "数据卡模板",
        ):
            if token not in agenda:
                errors.append(f"research-agenda appendix missing {token!r}")

    required_docs = {
        "docs/EVALUATION_MANIFEST_EXTENSION_V1.md": [
            "severity_factors:",
            "reference_distribution:",
            "container_digest:",
            "pollution_audit:",
            "query_budget:",
        ],
        "docs/templates/HUMAN_OBSERVER_PROTOCOL_TEMPLATE.md": ["伦理审批"],
        "docs/templates/DATA_CARD_TEMPLATE.md": ["Data Card"],
        "docs/GROK_BOOK_REVIEW_RESPONSE_20260713.md": ["本轮新增", "暂不在本轮扩写"],
    }
    for rel, tokens in required_docs.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        text = read(path)
        for token in tokens:
            if token not in text:
                errors.append(f"{rel} missing {token!r}")

    for rel in (
        ".github/workflows/one-shot-grok-book-review.yml",
        "tools/apply_grok_book_review_20260713.py",
    ):
        if (ROOT / rel).exists():
            errors.append(f"temporary remediation file still exists: {rel}")

    for error in errors:
        print(f"ERROR {error}")
    print(f"check_book_navigation: {len(errors)} error(s); {len(chapter_files)} chapters")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
