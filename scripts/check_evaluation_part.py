#!/usr/bin/env python3
"""Validate the restructured evaluation part and its frozen terminology."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CHAPTERS = BOOK / "chapters"

EXPECTED = [
    "chapters/15-unified-evaluation.qmd",
    "chapters/16-detectability-curves.qmd",
    "chapters/17-temporal-cross-model.qmd",
    "chapters/18-reliability-calibration.qmd",
    "chapters/19-cross-model-irt.qmd",
    "chapters/20-causal-standardization.qmd",
    "chapters/21-frontiers-ethics.qmd",
]

REQUIRED = {
    "15-unified-evaluation.qmd": [
        "\\mathcal E=\\langle O,X,T,P,M\\rangle",
        "Y^+",
        "Y^-",
        "N_{\\mathrm{FP}}",
        "三条评价轨道",
        "匹配误报工作点",
    ],
    "16-detectability-curves.qmd": [
        "R_{\\mathrm{ctrl}}",
        "R_{\\mathrm{std}}",
        "R_{\\mathrm{obs}}",
        "operatorname{dAUC}",
        "tau_{50",
        "v=1-o",
    ],
    "17-temporal-cross-model.qmd": [
        "T_{\\mathrm{FSD}}",
        "Kaplan",
        "右删失",
        "工作点不可匹配",
        "NWD",
    ],
    "18-reliability-calibration.qmd": [
        "risk–coverage",
        "weighted CP",
        "覆盖事件",
        "条件于已匹配",
        "查询重复性",
    ],
    "19-cross-model-irt.qmd": [
        "IRT-A",
        "IRT-B",
        "Rasch",
        "DIF",
        "固有属性",
    ],
    "20-causal-standardization.qmd": [
        "探索集",
        "确证集",
        "数字孪生",
        "SESOI",
        "camo-eval",
    ],
    "21-frontiers-ethics.qmd": [
        "前二十章",
        "两用风险",
        "开放治理",
    ],
}

FORBIDDEN = {
    "all": [
        "s50",
        "四个事实标准指标",
        "统一总分越高",
        "IRT 难度是目标固有",
        "J&F 就是时间稳定",
        "`boundary_iou`",
    ],
    "18-reliability-calibration.qmd": [
        "认知不确定性就是重复调用方差",
        "端到端目标检出覆盖保证为",
    ],
}

APPENDIX_REQUIRED = [
    "behavioral detectability",
    "predictive reliability",
    "R_{\\mathrm{ctrl}}",
    "tau_{50}",
    "IRT-A / IRT-B",
    "camo-eval/VALIDATION.md",
]

APPENDIX_FORBIDDEN = [
    "metrics: [mae, fw, sm, em, boundary_iou]",
    "事实标准指标",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def bibliography_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,]+),", text))


def citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for group in re.findall(r"\[@([^\]]+)\]", text):
        for token in re.findall(r"@?([A-Za-z0-9_:-]+)", group):
            keys.add(token)
    return keys


def main() -> int:
    errors: list[str] = []
    quarto = yaml.safe_load(read(BOOK / "_quarto.yml"))
    listed: list[str] = []
    for item in quarto["book"]["chapters"]:
        if isinstance(item, dict):
            listed.extend(item.get("chapters", []))
    for path in EXPECTED:
        if path not in listed:
            errors.append(f"_quarto.yml missing ordered chapter {path}")
        if not (BOOK / path).exists():
            errors.append(f"missing chapter file {path}")

    old_frontiers = CHAPTERS / "16-frontiers-ethics.qmd"
    if old_frontiers.exists():
        errors.append("superseded chapters/16-frontiers-ethics.qmd still exists")

    combined = ""
    for filename, tokens in REQUIRED.items():
        path = CHAPTERS / filename
        if not path.exists():
            continue
        text = read(path)
        combined += "\n" + text
        for token in tokens:
            if token not in text:
                errors.append(f"{filename} missing required token {token!r}")
        for token in FORBIDDEN.get("all", []):
            if token in text:
                errors.append(f"{filename} contains forbidden token {token!r}")
        for token in FORBIDDEN.get(filename, []):
            if token in text:
                errors.append(f"{filename} contains forbidden token {token!r}")

    appendix_path = CHAPTERS / "appendix-resources.qmd"
    appendix = read(appendix_path)
    combined += "\n" + appendix
    for token in APPENDIX_REQUIRED:
        if token not in appendix:
            errors.append(f"appendix-resources.qmd missing required token {token!r}")
    for token in APPENDIX_FORBIDDEN:
        if token in appendix:
            errors.append(f"appendix-resources.qmd contains forbidden token {token!r}")

    outline = read(ROOT / "docs/EVALUATION_PART_RESTRUCTURE_V1.md")
    evidence = read(ROOT / "docs/EVALUATION_PART_EVIDENCE_MATRIX_V1.md")
    audit = read(ROOT / "docs/EVALUATION_PART_SELF_AUDIT_V1.md")
    for token in (
        "第 15 章",
        "第 16 章",
        "第 17 章",
        "第 18 章",
        "第 19 章",
        "第 20 章",
    ):
        if token not in outline:
            errors.append(f"outline missing {token}")
    if "逐章证据清单" not in evidence:
        errors.append("evidence matrix title/identity missing")
    if "CLOSED-FOR-DRAFTING" not in audit:
        errors.append("self-audit not closed for drafting")

    bib = read(BOOK / "references.bib") + "\n" + read(BOOK / "evaluation-references.bib")
    known = bibliography_keys(bib)
    cited = citation_keys(combined)
    missing = sorted(cited - known)
    for key in missing:
        errors.append(f"evaluation part citation missing from bibliographies: {key}")

    for error in errors:
        print(f"ERROR {error}")
    print(
        f"check_evaluation_part: {len(errors)} error(s); "
        f"{len(EXPECTED)} chapters; {len(cited)} cited keys"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
