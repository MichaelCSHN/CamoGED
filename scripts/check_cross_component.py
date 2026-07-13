#!/usr/bin/env python3
"""Validate closure of the Awesome-discovered Book, Demo, and web follow-ups."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(text: str, label: str, tokens: tuple[str, ...], errors: list[str]) -> None:
    """Require at least one semantically equivalent token."""

    if not any(token in text for token in tokens):
        errors.append(f"{label} missing one of {tokens!r}")


def main() -> int:
    errors: list[str] = []

    appendix = read("book/chapters/appendix-resources.qmd")
    chapter10 = read("book/chapters/10-intelligent-overview-datasets.qmd")
    chapter14 = read("book/chapters/14-foundation-models.qmd")
    references = read("book/references.bib")
    factcheck = read("docs/BOOK_FACTCHECK_REGISTER.md")
    demo = read("web/demo.md")
    theme = read("web/.vitepress/theme/index.js")
    builder = read("scripts/build_awesome.py")
    backlog = read("docs/AWESOME_CROSS_COMPONENT_BACKLOG.md")

    for token in (
        "Awesome Camouflage",
        "Research Catalog",
        "verification_status",
        "metadata-only",
        "自动发现",
    ):
        if token not in appendix:
            errors.append(f"appendix missing {token!r}")

    chapter10_tokens = (
        "任务、监督与模态三轴谱系",
        "伪装目标跟踪",
        "弱监督",
        "半监督",
        "无监督",
        "零样本",
        "开放词汇",
        "视觉语言",
        "鲁棒性",
        "@rcod2025",
        "@cotd2024",
        "@mmcsbench2025",
    )
    for token in chapter10_tokens:
        if token not in chapter10:
            errors.append(f"chapter 10 missing {token!r}")
    require(chapter10, "chapter 10 bbox branch", ("bbox 型 RCOD", "bbox RCOD"), errors)
    for forbidden in ("当前最大图像基准", "跨数据集泛化评测标准"):
        if forbidden in chapter10:
            errors.append(f"chapter 10 retains unsupported wording {forbidden!r}")

    chapter14_tokens = (
        "@camsam2_2025",
        "@mmcsbench2025",
        "@sddf2026",
        "提示来源",
        "Research Catalog",
    )
    for token in chapter14_tokens:
        if token not in chapter14:
            errors.append(f"chapter 14 missing {token!r}")
    require(chapter14, "chapter 14 dynamic boundary", ("动态维护", "动态目录"), errors)
    for forbidden in ("性能保留率，普遍高于", "普遍高于使用专有 CNN"):
        if forbidden in chapter14:
            errors.append(f"chapter 14 retains unsupported wording {forbidden!r}")

    required_bib = {
        "rcod2025",
        "cotd2024",
        "scout2025",
        "ucoddpl2025",
        "camf2025",
        "ovcamo2023",
        "camsam2_2025",
        "mmcsbench2025",
        "sddf2026",
        "cod10kc2026",
    }
    found_bib = set(re.findall(r"@\w+\{([^,]+),", references))
    for key in sorted(required_bib - found_bib):
        errors.append(f"references missing {key!r}")

    for token in ("F15", "F16", "F17", "F18", "F19"):
        if token not in factcheck:
            errors.append(f"fact-check register missing {token}")

    for token in (
        "Research Catalog",
        "camo-eval/VALIDATION.md",
        "不自动接入",
        "代码与权重来源",
    ):
        if token not in demo:
            errors.append(f"demo guidance missing {token!r}")

    for component in ("CatalogExplorer", "AwesomeScanStatus"):
        if component not in theme:
            errors.append(f"VitePress theme does not register {component}")
        if not (ROOT / f"web/.vitepress/theme/components/{component}.vue").exists():
            errors.append(f"missing component {component}.vue")

    catalog_json = ROOT / "web/public/catalog.json"
    if not catalog_json.exists():
        errors.append("web/public/catalog.json was not generated")
    else:
        payload = json.loads(catalog_json.read_text(encoding="utf-8"))
        accepted = yaml.safe_load(read("data/papers.yaml"))["papers"]
        resources = payload.get("resources", [])
        if len(resources) != len(accepted):
            errors.append(
                f"catalog JSON count drift: json={len(resources)}, yaml={len(accepted)}"
            )
        if len({item.get("id") for item in resources}) != len(resources):
            errors.append("catalog JSON contains duplicate ids")
        for index, item in enumerate(resources):
            for field in (
                "id",
                "title",
                "authors",
                "year",
                "description",
                "resource_type",
                "tasks",
                "modalities",
                "supervision",
                "contexts",
                "verification_status",
            ):
                if field not in item:
                    errors.append(f"catalog JSON resource[{index}] missing {field}")

    if "catalog.json" not in builder or "<CatalogExplorer />" not in builder:
        errors.append("Awesome builder does not emit interactive catalog data/page")
    if "<AwesomeScanStatus />" not in builder:
        errors.append("Awesome builder does not emit live scan widget")

    if "Status: CLOSED" not in backlog:
        errors.append("cross-component backlog is not closed")

    readme = read("README.md")
    if "Awesome Camouflage" not in readme or "Research Catalog" not in readme:
        errors.append("root README does not explain Awesome/Catalog split")

    for error in errors:
        print(f"ERROR {error}")
    print(f"check_cross_component: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
