#!/usr/bin/env python3
"""Apply the first publication-grade editorial revision to the CamoGED monograph.

The script is intentionally conservative: it rewrites small front/back-matter files,
replaces explicitly identified placeholder sections, corrects known factual/technical
wording, and compresses chapter conclusions that had accumulated repetitive tails.
It does not invent experimental results or silently fill unverified tables.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG: list[str] = []


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel: str, text: str, note: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    CHANGELOG.append(f"- `{rel}`: {note}")


def replace(rel: str, old: str, new: str, note: str, *, required: bool = True) -> None:
    text = read(rel)
    if old not in text:
        if required:
            raise RuntimeError(f"Required text not found in {rel}: {old[:80]!r}")
        return
    write(rel, text.replace(old, new), note)


def regex_replace(
    rel: str,
    pattern: str,
    repl: str,
    note: str,
    *,
    flags: int = re.MULTILINE | re.DOTALL,
    required: bool = True,
    count: int = 0,
) -> None:
    text = read(rel)
    new, n = re.subn(pattern, lambda _match: repl, text, count=count, flags=flags)
    if n == 0:
        if required:
            raise RuntimeError(f"Required pattern not found in {rel}: {pattern[:100]!r}")
        return
    write(rel, new, f"{note}（命中 {n} 处）")


def replace_section(rel: str, start_heading: str, end_heading: str, body: str, note: str) -> None:
    pattern = rf"(?ms)^{re.escape(start_heading)}\n.*?(?=^{re.escape(end_heading)}\n)"
    replacement = f"{start_heading}\n\n{body.strip()}\n\n"
    regex_replace(rel, pattern, replacement, note)


# ---------------------------------------------------------------------------
# 1. Front matter, publication metadata, and build promises
# ---------------------------------------------------------------------------

write(
    "book/_quarto.yml",
    '''project:
  type: book
  output-dir: _book

book:
  title: "伪装：生成、识别与评价"
  subtitle: "自然、战争与机器的跨域综观"
  author:
    - name: "Michael C."
      role: "主编"
    - name: "CamoGED contributors"
      role: "协作者"
  date: "2026-07-13"
  date-format: "YYYY-MM-DD"
  repo-url: https://github.com/MichaelCSHN/CamoGED
  repo-actions: [edit, issue]
  search: true
  chapters:
    - index.qmd
    - part: "第一篇　伪装的前世今生"
      chapters:
        - chapters/01-essence-and-the-game.qmd
        - chapters/02-natural-camouflage.qmd
        - chapters/03-military-camouflage.qmd
        - chapters/04-camouflage-in-art.qmd
    - part: "第二篇　生成：隐藏方如何出招"
      chapters:
        - chapters/05-physical-generation.qmd
        - chapters/06-physical-adversarial.qmd
        - chapters/07-digital-generation.qmd
        - chapters/08-intelligent-generation.qmd
    - part: "第三篇　识别：揭示方如何反制"
      chapters:
        - chapters/09-physical-digital-detection.qmd
        - chapters/10-intelligent-overview-datasets.qmd
        - chapters/11-image-cod.qmd
        - chapters/12-video-cod.qmd
        - chapters/13-instance-extended.qmd
        - chapters/14-foundation-models.qmd
    - part: "第四篇　评价：如何裁定胜负"
      chapters:
        - chapters/15-unified-evaluation.qmd
        - chapters/16-frontiers-ethics.qmd
  appendices:
    - chapters/appendix-resources.qmd

bibliography: references.bib

execute:
  freeze: auto

format:
  html:
    theme: cosmo
    code-fold: true
    include-after-body: _includes/book-home-link.html
  pdf:
    documentclass: ctexbook
    pdf-engine: xelatex
    keep-tex: true
  epub:
    toc: true
''',
    "统一正式书名、篇章顺序、作者角色、版本日期，并配置 HTML/PDF/ePub 输出",
)

write(
    "book/index.qmd",
    '''# 前言 {.unnumbered}

本书讨论一种跨越自然科学、军事史、视觉文化与人工智能的共同问题：**目标如何降低被观察者察觉、定位或识别的概率，观察者又如何恢复被削弱的证据。** 我们把这类相互适应的问题称为“隐藏—揭示博弈”。这里的“博弈”首先是一套分析框架，而不是已经完成均衡证明的统一博弈论。

全书沿三项研究活动组织：**生成**讨论隐藏方如何改变目标的呈现；**识别**讨论揭示方如何利用传感器、算法、时间和语义恢复目标；**评价**讨论在明确观察者、信道、任务与协议的前提下，如何判断方法是否真正有效。自然、军事、艺术与机器视觉可以共享这套问题语言，但它们的历史因果、材料约束和效用函数并不相同。本书比较的是可检验的结构相似性，不主张不同领域的机制完全等同。

## 本书面向谁 {.unnumbered}

- 生物学、视觉生态和知觉研究者，可从第一篇与第15章进入；
- 材料、传感器和安全研究者，可重点阅读第3、5、6、9、15、16章；
- 计算机视觉研究者，可从第10章的任务与协议开始，再进入第11—14章；
- 研究生和工程人员，可使用代码单元、数据索引与 `camo-eval` 复现实例，但应把教学示意与真实实验严格区分。

## 证据与版本约定 {.unnumbered}

本书区分四类材料：一手论文、标准或档案；高质量专著与综述；项目复现结果；教学示意与研究议程。前三类可以支持不同强度的事实判断，教学示意只用于解释概念，不能替代真实数据实验。凡涉及“首个、最大、最强、当前”等时效性结论，均应给出检索范围与最后核验日期；未核实数字不进入正式比较表。

本版为公开编审版，版本日期为 **2026-07-13**。书稿、数据表与软件的完成度并不相同：正文只把已发表或已核验内容写成事实；尚未发表的作者项目仅作为研究议程出现，不预填架构、消融或性能数字。

::: {.callout-note}
## 活专著与正式版本
在线版本便于修订、执行代码和维护链接；正式发布版本将锁定正文、参考文献、图像版权、软件版本和引用信息。动态排行榜与项目路线以网站和机器可读数据为准，不在正文中手工维护易漂移的数字。
:::

::: {.callout-warning}
## 责任使用
军事伪装和对抗感知材料只用于解释机制、评价与防御，不提供针对现实部署系统的即用规避方案。项目的风险分级、数据限制与责任披露原则见 `ETHICS.md` 和第16章。
:::
''',
    "将项目公告式前言改写为正式前言，补充读者、证据等级、版本和责任边界",
)

write(
    "CITATION.cff",
    '''cff-version: 1.2.0
title: "CamoGED: Camouflage — Generation, Detection, and Evaluation"
message: "If you use CamoGED, please cite it using these metadata."
type: software
authors:
  - family-names: "C"
    given-names: "Michael"
repository-code: "https://github.com/MichaelCSHN/CamoGED"
url: "https://michaelcshn.github.io/CamoGED/"
abstract: >-
  CamoGED is a cross-domain open platform and living monograph on camouflage
  generation, detection, and evaluation across natural, military, cultural,
  physical, digital, and machine-perception settings. It includes the book,
  curated datasets and papers, reproducible evaluation tools, and research demos.
keywords:
  - camouflage
  - camouflaged object detection
  - adversarial camouflage
  - concealment
  - computer vision
  - evaluation
license: Apache-2.0
version: "0.2.0"
date-released: "2026-07-13"
''',
    "清除作者和发布日期占位项，更新项目标题与引用元数据",
)

# README: keep the project acronym while making the monograph order and release status honest.
replace(
    "README.md",
    "### Camouflage: **G**eneration · **E**valuation · **D**etection",
    "### Platform pillars: **G**eneration · **E**valuation · **D**etection",
    "区分项目品牌缩写与专著实际篇章顺序",
)
replace(
    "README.md",
    "> **Thesis.** Camouflage is a *co-evolutionary arms race* between a **hider** and a **seeker**.\n> The same structure recurs across biology (prey vs. predator), the military (measure vs. counter‑measure),\n> art (image vs. perception), and AI (generator vs. discriminator / attacker vs. detector).\n> CamoGED treats **generation** (hiding), **evaluation** (judging), and **detection** (seeking) as the three\n> faces of this single game — and unifies them into one living research platform.",
    "> **Working thesis.** Camouflage can be studied as an observer-, channel-, and task-dependent\n> interaction between a **hider** and a **seeker**, with evaluation defining what counts as success.\n> Biology, military engineering, visual culture, and AI share parts of this analytical structure,\n> while retaining different mechanisms, histories, constraints, and utility functions.",
    "将“完全同构”的强命题改为可检验的工作性命题",
)
replace(
    "README.md",
    "| 📚 **Monograph** | [`book/`](book/) | The book *Camouflage: Generation · Evaluation · Detection* (Quarto → HTML/PDF/ePub) |",
    "| 📚 **Monograph** | [`book/`](book/) | *Camouflage: Generation, Detection, and Evaluation*; HTML is CI-gated, while PDF/ePub remain release outputs requiring format-specific proofing |",
    "修正专著标题并如实说明多格式成熟度",
)
replace(
    "README.md",
    "# Evaluation toolkit (one working metric ships now: MAE; others scaffolded)",
    "# Evaluation toolkit (core COD, boundary, video, perceptual and signature metrics are implemented; heavy generation metrics remain optional)",
    "同步 camo-eval 当前实现状态",
)
replace(
    "README.md",
    "If CamoGED helps your work, please cite it via [`CITATION.cff`](CITATION.cff) (a versioned DOI is minted on each release).",
    "If CamoGED helps your work, please cite it via [`CITATION.cff`](CITATION.cff). A DOI will be added when a release is archived in a DOI-minting repository.",
    "移除尚未兑现的 DOI 自动生成承诺",
)

write(
    ".github/workflows/book.yml",
    '''name: book

# Render the portable online formats as CI gates. PDF remains a release-format
# proofing task because it requires a pinned Chinese TeX/font environment.
on:
  push:
    branches: [main]
    paths: ["book/**", ".github/workflows/book.yml"]
  pull_request:
    paths: ["book/**", ".github/workflows/book.yml"]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        format: [html, epub]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Python dependencies for executable cells
        run: pip install jupyter numpy matplotlib scipy

      - uses: quarto-dev/quarto-actions/setup@v2

      - name: Render book
        run: quarto render book --to ${{ matrix.format }}

      - uses: actions/upload-artifact@v4
        with:
          name: book-${{ matrix.format }}
          path: book/_book
''',
    "将 HTML 与 ePub 纳入 PR/主分支 CI，并明确 PDF 需独立中文排版校样",
)

# ---------------------------------------------------------------------------
# 2. Editorial governance documents
# ---------------------------------------------------------------------------

write(
    "docs/BOOK_STYLE_GUIDE.md",
    '''# CamoGED 专著体例与文字规范

## 1. 体裁定位

本书定位为“跨学科研究专著 + 可执行附录”。正文承担概念、证据、方法、争议与评价；CLI、API、在线 Demo、文件结构和开发路线放入项目文档。软件只作为可复现实证锚点，不主导全书叙述。

## 2. 核心术语

- 全书角色统一称为 **隐藏方（hider）**、**揭示方（seeker）**、**评价者（judge/evaluator）**。
- “攻击方/守方”只在具体安全或军事语境中使用，不作为跨域总称。
- “识别”是上位过程；检测、定位、分割、分类、跟踪是具体任务。
- COD 指图像伪装目标像素级分割时，应说明这是社区约定名称，避免与一般目标检测混淆。
- “智能域”只在三域框架中使用；具体章节优先写“学习式生成”“基础模型适配”等可检验术语。

## 3. 论证强度

- “首次、唯一、最大、最强、当前”等词必须附检索范围、截止日期和一手来源。
- 无法完成穷尽检索时，使用“据本书截至某日对……的检索，尚未发现”。
- “证明”仅用于严格理论或充分实验；综述和案例通常使用“表明、支持、提示”。
- “同构”仅在映射对象、关系和保真范围均被明确时使用；一般跨域比较写“结构相似”或“可作有限类比”。

## 4. 章节体例

每章采用：导读 → 问题与证据 → 方法或案例 → 局限与争议 → 小结 → 延伸阅读。

- 每章只保留一个小结，控制在 3—5 段。
- 小结只回答：本章建立了什么、仍不确定什么、下一章如何接续。
- 小结后不得再出现第二轮论证或多组一行一段的口号式尾句。
- 跨章框架回扣优先使用一张“观察者—信道—任务—评价”卡片，不重复长篇解释 H/S/C/U。

## 5. 引用与证据等级

- P：一手论文、标准、档案、官方数据；
- S：权威专著和系统综述；
- T：预印本、项目页、技术报告、演示材料。

关键事实、历史“首次”和正式性能比较至少需要一条 P 级证据。T 级来源必须标明预印本或临时状态。

## 6. 动态内容

数据集、排行榜和软件实现只从机器可读数据或版本化接口生成。正文仅渲染 `verified: true` 的记录，并保存 `last_verified`、协议、来源和实现版本。未核实条目进入网站待核验区，不进入正式事实表。

## 7. 代码与图表

- 玩具代码统一标为“教学示意”，不得写成真实机制复现或有效性证明。
- 图表应给出数据、生成脚本、版本和许可。
- 历史图片、艺术作品、动物摄影和军事图像必须建立版权清单；无许可时采用公版、开放许可或原创改绘。
- 图表中的缩写、箭头方向、指标升降方向和配色含义全书统一。

## 8. 数字与格式

- 中英文术语首次出现时给出中文、英文和缩写；后文使用统一简称。
- 数字与单位之间留空格；百分数、区间、均值±标准差采用统一格式。
- 指标首次出现注明 ↑/↓；报告均值时同时给出方差、区间或重复次数。
- 中文使用全角标点；公式、代码和路径使用半角标点。

## 9. 出版验收

HTML、PDF、ePub 分别验收。HTML 检查链接、交叉引用和移动端；PDF 检查中文字体、跨页表格、代码溢出和图像分辨率；ePub 检查目录、公式、脚注和宽表降级。任何格式通过均不能替代其他格式校样。
''',
    "新增正式体例、术语、证据、动态数据和多格式出版规范",
)

write(
    "docs/BOOK_SEARCH_METHODOLOGY.md",
    '''# 文献检索与纳入方法

本文件用于支撑书稿中的“尚未发现同类专著”“首个数据集”“当前主要基准”等结论。它是可更新的检索记录，而不是一次性宣传材料。

## 检索范围

- 学术数据库：Web of Science、Scopus、Google Scholar、Crossref、Semantic Scholar；
- 图书与馆藏：WorldCat、主要大学出版社目录、国家图书馆目录；
- 标准与官方资料：NIST、NATO/STO、政府审计与军种公开资料；
- 计算机视觉：CVF Open Access、IEEE Xplore、ACM Digital Library、SpringerLink、arXiv；
- 项目与数据：论文官方项目页、作者仓库、数据集发布页。

## 核心检索组

1. camouflage / crypsis / masquerade / mimicry / concealment；
2. military camouflage / signature management / target acquisition；
3. camouflage art / dazzle / camoufleurs / visual perception；
4. camouflaged object detection / concealed object segmentation / video camouflage；
5. adversarial camouflage / physical adversarial attack；
6. camouflage evaluation / detectability / visual search / human factors。

每组分别与 book、handbook、survey、dataset、benchmark、evaluation、generation、detection 等组合检索。中文检索同步使用“伪装、隐蔽、拟态、迷彩、伪装目标检测、伪装评价”等词。

## 纳入与排除

纳入：正式专著、同行评审论文、标准、公开技术报告、可核验数据集和方法项目。预印本可以纳入前沿讨论，但必须标明状态。排除：无法追溯来源的媒体转述、只有营销演示而无方法说明的项目、重复发布版本、无法确认许可或身份的镜像资源。

## 结论用语

穷尽性结论统一写为：

> 据本书截至 YYYY-MM-DD 对上述数据库、关键词和语种范围的检索，尚未发现……

“首个、最大、当前”等结论必须在 `docs/BOOK_FACTCHECK_REGISTER.md` 中留下核验记录，并在版本发布前重新检索。

## 当前核验日期

本轮编审基准日期：**2026-07-13**。后续发布版本必须更新该日期，并记录新增或改变结论的来源。
''',
    "新增可审计的检索范围、关键词、纳入标准和结论用语",
)

write(
    "docs/BOOK_FACTCHECK_REGISTER.md",
    '''# 专著事实核查登记表

状态：`OPEN` 待核；`REVISED` 已降格或改写；`VERIFIED` 已由一手来源核验；`DEFERRED` 移出正式正文。

| ID | 位置 | 原问题 | 本轮处理 | 状态 | 发布前要求 |
|---|---|---|---|---|---|
| F01 | 全书定位 | “四领域完全同构”“唯一/首次”过强 | 改为工作性分析框架，要求限定检索范围 | REVISED | 发布前更新检索日期 |
| F02 | 第1章 | H/S/C/U 被表述为完整博弈论 | 明确其为分析框架，非均衡理论 | REVISED | 理论扩展另行同行评审 |
| F03 | 第3章 UCP | 以早期图录支持后续替换史 | 改为审慎叙述并列入核查 | OPEN | 补美国陆军/GAO一手资料 |
| F04 | 第5章热红外 | “与反射率无关、完全由温度与发射率决定” | 改为包含自身辐射、环境反射、大气与传感器响应 | REVISED | 红外专业审校 |
| F05 | 第10章 NC4K | “真正意义上的 OOD”缺乏数据重叠审计 | 改为“较强分布差异测试” | REVISED | 做重复样本与来源审计 |
| F06 | 第10章泄漏 | “贡献 1—5% 虚假提升”无来源 | 删除定量断言 | REVISED | 有实证后再恢复 |
| F07 | 第14章 | “第三篇九章”计数错误 | 改为六章 | VERIFIED | — |
| F08 | 第14章 CLIP | 将全局图文对齐直接写成像素定位 | 改为语义检索信号，定位需稠密化/适配 | REVISED | 检查后续所有 CLIP 表述 |
| F09 | 第14章适配 | SAM 原论文误作 Adapter 引文 | 改为参数高效适配并引用对应工作 | REVISED | 补完整方法谱系 |
| F10 | 第12/15章 | J&F 与时间稳定性混同风险 | 明确 J/F 为区域/边界，稳定性单列 | REVISED | 核验工具实现与命名 |
| F11 | 原创项目 | coder/flowcamo/dualvcod 无结果占位 | 压缩为研究议程，删除空表和预填承诺 | DEFERRED | 论文定稿后按标准协议回填 |
| F12 | 数据表 | `—`、预印本、未核许可证混入正文 | 附录增加核验字段和正式表准入规则 | OPEN | 仅渲染 verified 条目 |
| F13 | 出版信息 | 作者、日期、DOI、格式承诺为占位 | 更新版本元数据，移除未兑现 DOI 承诺 | REVISED | 正式发布时补 ORCID/DOI |
| F14 | 图像版权 | 缺少逐图来源与许可台账 | 纳入附录与体例要求 | OPEN | 发布前逐图清账 |

## 责任分工原则

跨学科事实不由单一编辑最终裁定：生物学、军事史、红外/材料、对抗机器学习、COD 协议和出版版权分别需要领域审校。编辑负责记录问题、控制措辞、验证引文是否支持结论，并阻止未核内容进入正式表格。
''',
    "新增逐项事实核查台账并记录本轮处理状态",
)

# ---------------------------------------------------------------------------
# 3. Chapter-level conceptual corrections and placeholder removal
# ---------------------------------------------------------------------------

# Chapter 1: clarify the framework's epistemic status and remove strict zero-sum claims.
replace(
    "book/chapters/01-essence-and-the-game.qmd",
    "这不是一个比喻，而是一个可复用的结构。把它形式化（@fig-game）：一场伪装博弈可记为",
    "这里的“博弈”首先是一套可复用的**分析框架**：它帮助比较角色、信道与效用，但尚未给出完整的策略空间、信息结构和均衡理论。为便于后文标定问题，一场隐藏—揭示互动可暂记为",
    "将 H/S/C/U 从完整博弈论降格为工作性分析框架",
)
replace(
    "book/chapters/01-essence-and-the-game.qmd",
    "其三，$\\mathcal{G}$ 是一个**零和或近零和**的对抗结构，这正是它能被写成 GAN 的极小极大目标、被写成对抗攻防的攻击—防御循环的根本原因。",
    "其三，在漏检率、命中率或模型损失等特定任务指标上，双方可以被近似写成对抗目标；但自然、军事、艺术和社会场景通常还包含成本、合作、身份与多重效用，不能一概视为严格零和。",
    "删除跨域严格零和断言",
)
replace_section(
    "book/chapters/01-essence-and-the-game.qmd",
    "## 1.10 小结 {#sec-01-summary}",
    "## 延伸阅读与链接 {#sec-01-further}",
    '''本章建立了全书的工作语言：任何伪装问题都应先说明隐藏方、揭示方、观测信道和评价效用；“察觉”与“识别”是两个相关但不同的失败环节；物理、数字与学习式方法可以共享部分分析坐标，但不能因此抹平领域差异。

$\\mathcal{G}=\\langle H,S,C,U\\rangle$ 在本书中是组织和比较问题的框架，而不是已经证明均衡性质的统一博弈论。后续章节使用它时，必须保留观察者、材料、历史和任务的具体约束。

第2章将从自然伪装进入具体机制，并以目标观察者和可重复实验检验这些机制，而不是把动物案例仅作为技术隐喻。''',
    "压缩第1章结论并明确理论边界",
)

replace_section(
    "book/chapters/02-natural-camouflage.qmd",
    "## 2.11 小结 {#sec-02-summary}",
    "## 延伸阅读 {#sec-02-further}",
    '''自然伪装不是单一外观，而是目标、背景、行为、信道和观察者之间的关系。背景匹配、瓦解色、消影、透明或反射、伪装性拟态和运动策略攻击不同的感知线索，真实动物通常组合多种机制，并受能量、繁殖、行为和环境约束。

评价必须面向真实或明确的代理观察者。视觉模型、野外捕食实验与人类视觉搜索各有证据强度和外推边界，不能由一张“看起来很像背景”的照片替代。

下一章讨论人类如何把这些机制工程化并嵌入组织、传感器和任务链。跨域比较的重点是机制与失败模式，而不是宣称自然选择和人工设计具有相同历史原因。''',
    "压缩第2章反复回扣并保留生物学方法论结论",
)

# Chapter 3: soften the UCP case and compress the conclusion.
regex_replace(
    "book/chapters/03-military-camouflage.qmd",
    r"但数字迷彩史上最重要的一课，恰是一次\*\*失败\*\*。美国陆军于 2004 年前后列装的“通用迷彩图案（UCP）”.*?这正是第 1\.6\.2 节“观察者依赖性”的代价，也是本书把“评价”立为独立第四篇的现实注脚（前向呼应第 15 章）。",
    '''UCP 的服役争议与后续替换过程，是“通用图案必须接受真实环境评测”的重要案例。现有公开材料表明，部队反馈、补充测试与采购决策共同推动了图案调整；但其设计选择、测试过程和不同环境表现不能由单一图录或轶事概括。本书因此只把 UCP 作为评价覆盖不足的案例，不把它简化为“像素迷彩必然失败”或“某一机制单独导致失败”。相关官方资料仍列入事实核查登记表，正式发布前补齐。''',
    "删除由早期图录支撑后续 UCP 结论的过强叙述",
)
replace_section(
    "book/chapters/03-military-camouflage.qmd",
    "## 3.9 小结 {#sec-03-summary}",
    "## 延伸阅读 {#sec-03-further}",
    '''军事伪装把自然界的若干视觉机制转化为材料、图案、组织和欺骗系统，并随着观测距离与传感器扩展，从可见光背景匹配走向多谱段特征管理。其评价对象也由单件物体扩展到发现时间、目标获取距离、识别层级、资源消耗和任务结果。

本章的关键限制是：历史效果往往难以用受控实验归因，公开资料也不能代表完整作战性能。因此，历史案例用于解释问题与评价困难，不用于推导针对现实装备的操作参数。

第4章将集中讨论艺术、格式塔与文化意义；材料机理和制造约束则在第5章展开，避免军事史章节承担重复的材料教材功能。''',
    "压缩第3章结语并明确历史证据边界和跨章分工",
)

replace_section(
    "book/chapters/04-camouflage-in-art.qmd",
    "## 4.7 给本书框架的启示与小结 {#sec-04-summary}",
    "## 延伸阅读 {#sec-04-further}",
    '''艺术与视觉文化揭示了伪装的认知维度：观者并非被动接收像素，而会依据边界、闭合、深度、运动、语义和文化先验组织图像。错视、双关图像、眩惑迷彩和反监控设计分别作用于不同环节，不能被笼统地归为同一种“看不见”。

艺术中的效用还可能是延迟识别、揭示过程、审美震动或政治表达，因而不能直接套用生存率、目标获取距离或分割指标。可比较的是观察者如何被引导或误导，而不是把文化意义压缩为一个隐蔽分数。

第一篇至此完成问题定义。第二篇开始讨论隐藏方如何在物理、数字和学习式系统中生成具体策略。''',
    "压缩第4章结论并保留艺术评价的独立性",
)

# Chapter 5: correct thermography and replace the overgrown final section.
replace(
    "book/chapters/05-physical-generation.qmd",
    "热红外（8–14 μm）探测的是物体自身的热辐射，与反射率无关，完全由**温度与发射率**决定（由基尔霍夫辐射定律支配）。其可见光与近红外迷彩对热红外完全透明——你在热像仪里看到的，是物体的温度分布，与它涂了什么颜色无关。",
    "热红外（典型长波窗口约 8–14 μm）记录的是到达传感器的谱段辐射，其中既有目标自身发射，也可能包含环境辐射的反射、大气传输和传感器响应。表面温度与谱段发射率是关键变量，但低发射率表面的反射背景会显著影响表观温度；可见光颜色也不能直接推出热红外表现。",
    "纠正热像辐射并非只由温度和发射率决定的过度简化",
)
replace_section(
    "book/chapters/05-physical-generation.qmd",
    "## 5.7 多目标权衡的形式化与本章小结 {#sec-tradeoff}",
    "## 延伸阅读 {#sec-05-further}",
    '''物理域伪装生成可以概括为受制造约束的多目标优化：

$$
\\min_{\\mathbf d,\\mathbf m}\;[C_{\\rm vis},C_{\\rm nir},C_{\\rm ir},C_{\\rm rcs},C_{\\rm cost}]
\\quad \\text{s.t.}\\quad g_{\\rm mfg}(\\mathbf d,\\mathbf m)\\le 0.
$$

$\\mathbf d$ 表示图案和几何设计，$\\mathbf m$ 表示材料参数。各代价函数对应不同观察者与信道，量纲和任务后果并不相同，因此不能未经说明地相加为一个“总隐蔽分数”。真实方案是在明确威胁优先级后选择可制造、可维护的折中。

本章把生物机制转译为颜色、纹理、边界、光照、材料、曲面和制造问题。屏幕上的二维效果只是设计输入；部署结论必须经过光谱、热、几何、时间和制造误差测试。

第6章在同一物理约束上加入机器检测器这一特定观察者，讨论对抗优化为何比普通图案生成更容易过拟合模型和仿真信道。''',
    "保留多目标公式，删除章末多轮口号式收尾",
)

# Chapter 7: clarify that this is a book-specific taxonomy.
replace(
    "book/chapters/07-digital-generation.qmd",
    'title: "数字域伪装生成"',
    'title: "数字域的隐藏与欺骗"',
    "将数字章节从笼统‘伪装生成’改为更准确的隐藏与欺骗",
)
replace(
    "book/chapters/07-digital-generation.qmd",
    "数字域里，\"隐藏\"的对象不再只是物体。本章讲解三类性质不同却共享同一博弈骨架的数字伪装",
    "数字域里，‘隐藏’的对象不再只是物体。本章采用一套**工作性分类**，并置三类性质不同的数字隐藏与欺骗；它们并非既有学科中公认的同一任务族，只因都要求明确隐藏对象、揭示方与传播信道而放在同一章比较",
    "明确隐写、Deepfake 与数字对抗是本书工作性并置而非公认统一门类",
)
replace_section(
    "book/chapters/07-digital-generation.qmd",
    "## 7.7 小结 {#sec-07-summary}",
    "## 延伸阅读 {#sec-07-further}",
    '''隐写、Deepfake 与语义对抗隐藏的对象、面对的揭示方和评价协议均不相同。隐写关心秘密恢复与统计不可检测，Deepfake 关心身份、来源和跨媒体一致性，语义对抗关心模型决策变化与人类语义保持。把三者并置的价值在于防止指标错配，而不是把它们压成同一技术类别。

数字域没有印刷和天气噪声，却有压缩、转码、平台处理、传播语境和模型更新。任何数字隐藏结论都应报告经过哪些后处理、面对何种检测器，以及是否跨生成器或跨平台成立。

第9章将从揭示方角度讨论相应的统计分析、媒体取证和鲁棒防御。''',
    "压缩第7章二次收尾并强化三类任务边界",
)

# Chapter 8: replace unpublished flowcamo placeholder with a short research agenda.
replace_section(
    "book/chapters/08-intelligent-generation.qmd",
    "## 8.7 [原创] flowcamo：运动感知的视频伪装生成 {#sec-08-flowcamo}",
    "## 8.8 生成-检测闭环：让两手相互磨砺 {#sec-loop}",
    '''### 作者研究议程：视频生成

视频生成相较单图增加了运动对齐、纹理连续、遮挡变化和标注传播问题。逐帧生成即使单帧自然，也可能产生闪烁或不一致的运动边界，因此未来研究应把光流或其他时序对应关系作为约束，并在真实视频测试集上检查合成数据是否改善检测泛化。

作者项目 `flowcamo` 尚未形成可公开核验的架构、消融和结果，本版不把设计意图写成既成方法。项目状态、实验计划和代码入口保留在 `projects/flowcamo`；只有在论文与复现实验定稿后，才按第10章协议和第15章指标回填正式方法内容。''',
    "将未发表 flowcamo 长篇占位压缩为有边界的研究议程",
)
replace_section(
    "book/chapters/08-intelligent-generation.qmd",
    "## 8.9 小结与第二篇总结 {#sec-08-summary}",
    "## 延伸阅读 {#sec-08-further}",
    '''学习式生成把固定图案搜索扩展为样本分布和条件策略学习。经典融合、GAN、扩散模型与风格迁移分别擅长局部统计、快速采样、高质量条件生成和特征统计重组，但视觉真实性不等于伪装价值，也不等于训练收益。

生成增强必须保留可靠标注，以传统增强和无增强模型为对照，并只在独立真实测试集上判断收益。合成比例、难例类型、生成伪迹和跨数据集表现应同时报告。

第二篇由此完成从材料到对抗纹理、数字隐藏和学习式生成的展开。第三篇将转向揭示方，并首先讨论换信道和融合证据。''',
    "压缩第二篇总结并删除项目路线式重复段落",
)

# Chapter 10: remove unsupported quantitative leakage claim and OOD absolutism.
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "这使它与训练集有更大的分布差异，是真正意义上的\"分布外\"泛化评测。",
    "这通常使它与训练集具有更明显的来源和分布差异，可作为跨数据集泛化测试；但在完成重复样本和来源重叠审计前，不宜把它称为严格的分布外数据。",
    "将 NC4K 从严格 OOD 降格为跨数据集泛化测试",
)
regex_replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    r"这些泄漏来源在论文中几乎从不报告，但它们可能贡献 1–5% 的虚假性能提升，足以制造错误的方法排名。",
    "这些泄漏来源在论文中往往报告不足，且足以改变小数点竞争中的方法排序；在缺少专门实证时，本书不预设统一的影响百分比。",
    "删除无来源的 1—5% 泄漏增益断言",
)
replace_section(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "## 10.8 小结 {#sec-10-summary}",
    "## 延伸阅读 {#sec-10-further}",
    '''第10章规定了后续方法比较的最低条件：先定义任务，再说明数据、预训练、提示、推理与后处理协议，最后选择与失败模式匹配的指标。标准协议、扩展数据和基础模型结果应分档报告，不能混排为单一排行榜。

数据集不仅要记录规模，还要记录来源、划分、标注粒度、许可证、难度结构、负样本、多目标、视频序列和多模态配准。动态表格只从机器可读元数据生成；未核验条目不得进入正式比较。

下一章在这些规则下梳理图像 COD 方法。读者应持续区分结构贡献、骨干贡献、额外数据贡献和协议差异。''',
    "压缩第10章重复的‘规则是地基’尾段",
)

# Chapter 11: replace coder placeholder and empty table, then create a concise method synthesis.
replace_section(
    "book/chapters/11-image-cod.qmd",
    "## 11.7 [原创] coder：图像 COD 原创方法 {#sec-coder}",
    "## 11.8 方法演进的主线 {#sec-thread}",
    '''### 作者研究议程：可复现图像 COD 基线

作者计划以 `coder` 作为图像 COD 的可复现研究基线，但本版不包含未经论文和独立复现核验的架构、消融或性能表。项目只有在满足第10章标准训练协议、提供三套测试集完整指标、公开预测掩膜和固定评测命令后，才可作为正式原创方法写入正文。

当前项目入口和开发状态保留在 `projects/coder`。正文只保留这一研究边界，不以空 SOTA 表或未来式实现要求占用方法综述篇幅。''',
    "将 coder 长篇占位与空 SOTA 表压缩为研究议程",
)
replace_section(
    "book/chapters/11-image-cod.qmd",
    "## 11.8 方法演进的主线 {#sec-thread}",
    "## 延伸阅读 {#sec-11-further}",
    '''图像 COD 的方法演进可以沿“证据范围”理解：传统方法使用局部颜色、纹理和频率；CNN 以多尺度和粗到细流程建立目标假设；Transformer、图网络和状态空间模型扩展长程关系；频域和边界支路补充弱统计证据；弱监督与合成数据则改变标注和训练条件。

这些路线没有单一胜者。局部细节与全局语义、背景抑制与目标召回、模型能力与计算成本之间始终存在权衡。任何模块都应对应明确失败模式，并用相应分组、边界证据或效率指标验证，而不能只依靠总体平均分。

第12章加入时间维度。视频方法是否真正进步，取决于它如何使用运动、对齐和记忆，而不是简单把更多帧堆入网络。''',
    "删除第11章多轮方法宣言和一行式视频过渡",
)

# Chapter 12: replace flowcamo placeholder and clarify video metrics in the conclusion.
replace_section(
    "book/chapters/12-video-cod.qmd",
    "## 12.6 [原创] flowcamo：运动感知的视频伪装检测 {#sec-12-flowcamo}",
    "## 12.7 小结与主线回扣 {#sec-12-summary}",
    '''### 作者研究议程：运动—外观联合检测

`flowcamo` 的检测分支拟研究运动线索、外观筛选和时序稳定之间的关系，但当前没有可核验的正式结果。本版不预设双路架构必然有效，也不把生成—检测闭环写成已完成系统。

未来回填需至少比较逐帧图像 COD、显式光流、无光流时空模型和基础模型适配；明确在线/离线、提示来源、光流成本与序列划分；同时报告区域 $\\mathcal J$、边界 $\\mathcal F$、独立的时间稳定性和长序列失败案例。项目状态见 `projects/flowcamo`。''',
    "将 flowcamo 检测分支占位压缩为可验收研究议程",
)
replace_section(
    "book/chapters/12-video-cod.qmd",
    "## 12.7 小结与主线回扣 {#sec-12-summary}",
    "## 延伸阅读 {#sec-12-further}",
    '''视频为揭示方增加了运动、持续观察和重捕获证据，也引入背景动态、相机运动、对齐误差和错误记忆。方法的核心差异在于时间被用于候选发现、特征对齐、输出稳定、遮挡恢复还是身份维护。

$\\mathcal J$ 与 $\\mathcal F$ 分别评价区域和边界，二者汇总不能替代时间稳定性。视频结果还必须说明在线或离线、是否使用人工首帧提示、序列划分、帧率、光流或记忆成本，并展示闪烁、漂移、遮挡后丢失和重捕获失败。

第13章从时间扩展到对象与语义：当场景中有多个目标时，二值前景不足以表示实例、身份和语言所指。''',
    "统一视频指标解释并删除重复过渡尾句",
)

# Chapter 13: replace dualvcod placeholder and trim the repetitive final tail while retaining task tables.
replace_section(
    "book/chapters/13-instance-extended.qmd",
    "## 13.4 [原创] dualvcod：视频伪装实例检测 {#sec-dualvcod}",
    "## 13.5 指代伪装检测 {#sec-referring}",
    '''### 作者研究议程：视频实例与身份保持

`dualvcod` 拟研究视频中多个伪装实例的分离和跨帧身份保持。该问题需要同时评价逐帧实例掩膜、轨迹完整性、ID switch、遮挡后重识别和计算代价，不能由二值 VCOD 指标替代。

当前架构、消融和结果尚未形成可公开核验的论文版本，因此本版不展开双路径设计，也不预填比较数据。正式回填应明确实例级数据来源、序列级划分、ID 匹配协议和与图像 CIS、视频语义 COD 的增量。项目状态见 `projects/dualvcod`。''',
    "将 dualvcod 占位压缩为视频实例研究议程",
)
regex_replace(
    "book/chapters/13-instance-extended.qmd",
    r"本章的最终结论是：扩展任务不是 COD 的边缘分支.*?(?=^## 延伸阅读)",
    '''本章的结论是：扩展任务把“发现前景”推进到分清个体、保持身份、理解语言、利用图组和处理未见类别。每一种能力都需要新的标注、负样本和评价协议；二值 mask 指标不能代替实例、轨迹、指代或开放词汇结果。

第14章讨论基础模型如何提供通用分割、语义和视频记忆能力，同时检验这些能力在弱显著目标上的系统性盲点。\n\n''',
    "删除第13章结论后的多轮重复收束和单句尾段",
)

# Chapter 14: correct chapter count, CLIP localization, and overclaim in the heading.
replace(
    "book/chapters/14-foundation-models.qmd",
    "## 14.1 范式转变：为何\"通用底座 + 适配\"优于从头训练 {#sec-paradigm}",
    "## 14.1 范式转变：为何“通用底座 + 适配”成为重要路线 {#sec-paradigm}",
    "将基础模型优势改为条件性路线判断",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "给定文本描述\"a camouflaged frog on tree bark\"，CLIP 可以在图像中定位匹配区域，而无需任何伪装标注。",
    "给定文本描述“a camouflaged frog on tree bark”，原始 CLIP 可以提供图像级语义检索信号；要形成可靠的区域或像素定位，还需要 patch 级特征、稠密预测头、可视化方法或与分割模型结合。",
    "纠正原始 CLIP 可直接定位目标的表述",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "**SAM-Adapter** 类方法在 SAM 编码器的各层之后插入轻量适配器（Adapter）[@kirillov2023sam]",
    "**参数高效适配**方法在冻结或部分冻结 SAM 主干的前提下插入轻量 Adapter；其代表性 COD 实现应引用对应适配论文，而不是把 SAM 原论文作为 Adapter 证据。双流适配器提供了一个明确实例[@dualstream2025]",
    "修正 SAM 原论文误作 Adapter 方法引文",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "九章（Ch9–Ch14）覆盖了揭示方",
    "六章（Ch9–Ch14）覆盖了揭示方",
    "修正第三篇章数错误",
)
replace_section(
    "book/chapters/14-foundation-models.qmd",
    "## 14.8 小结与第三篇总结 {#sec-14-summary}",
    "## 延伸阅读 {#sec-14-further}",
    '''基础模型为 COD 带来通用对象性、分割、语义、视频记忆和语言解释能力，但其预训练分布通常偏向显著目标。SAM/SAM2 的瓶颈常在自动提示和错误传播，CLIP 的瓶颈在弱目标的语义稀释与空间定位，DINO 类特征仍会被强背景对象性吸引，MLLM 则面临定位粗糙和幻觉。

基础模型结果必须单列模型版本、权重来源、冻结策略、提示协议、额外数据、人工成本、后处理和计算代价。人工框提示、自动发现和零样本结果不能混排；更大预训练规模也不能自动归因于 COD 专用模块。

第三篇由此形成六章：第9章扩展信道，第10章固定任务与协议，第11章处理单图结构，第12章加入时间，第13章加入实例和语义，第14章组织通用基础能力。第15章将检验这些能力扩展是否在可比协议下带来真实收益。''',
    "压缩第三篇总结并突出基础模型实验分档",
)

# Chapter 15: refine the channel term and compress the ending.
replace(
    "book/chapters/15-unified-evaluation.qmd",
    "$X$ 是 channel（信道，即第 1 章博弈框架中的 $C$），包括 RGB、红外、雷达、多光谱、视频、文本提示等；",
    "$X$ 是输入或观测信道，包括 RGB、红外、雷达、多光谱及视频；文本提示属于任务输入条件，应在 $T$ 或 $P$ 中说明，而不与物理传感信道混为一类；",
    "区分物理/数据输入信道与文本提示条件",
)
replace_section(
    "book/chapters/15-unified-evaluation.qmd",
    "## 15.7 小结 {#sec-15-summary}",
    "## 延伸阅读 {#sec-15-further}",
    '''统一评价不是寻找一个跨生物、军事和机器视觉的万能分数，而是统一报告逻辑：明确观察者、输入信道、任务、协议和指标，并保存不确定性、失败样本和复现条件。不同任务可以使用不同指标，但不能省略其适用边界。

识别评价需要像素、结构、边界、实例和视频层级；生成与对抗评价必须把真实性、任务影响和跨变换鲁棒性成对报告；人因与目标获取实验还需控制被试、学习、距离、传感器和统计功效。单一均值、单一模型或未披露人工提示都不足以支撑广泛结论。

`camo-eval` 的角色是把稳定指标、协议 manifest、结果导出和失败可视化写成可执行约束。重型生成指标、人因实验和外场任务由扩展模块或外部系统执行，核心库负责记录、汇总和版本化，而不假装所有评价都能化为一个 Python 函数。''',
    "删除第15章多轮终句并保留五元组和工具边界",
)

# Chapter 16: soften active-sensing absolutism and replace the overgrown conclusion.
replace(
    "book/chapters/16-frontiers-ethics.qmd",
    "一个能移动的检测智能体，等效于拥有无穷多个信道的揭示方，使守方\"只针对有限信道优化\"的防御策略原则上失效。",
    "一个能移动的检测智能体可以主动改变视角、距离与传感器配置，显著扩展可获得的观测集合；但它仍受可达空间、时间、能耗、遮挡和传感器能力限制，不能等同于拥有无穷信道。",
    "删除具身揭示方拥有无穷信道的绝对化比喻",
)
replace_section(
    "book/chapters/16-frontiers-ethics.qmd",
    "## 16.7 全书结语 {#sec-conclusion}",
    "## 延伸阅读 {#sec-16-further}",
    '''本书把伪装定义为一种关系：目标通过外观、材料、行为、信息或模型策略改变观察者获得和组织证据的难度。自然、军事、艺术和机器视觉可以共享“谁在隐藏、谁在观察、通过什么信道、执行什么任务、如何评价”的问题语言，但其机制、历史和责任边界不能相互替代。

第一篇建立机制与观察者视角；第二篇讨论物理、数字和学习式生成；第三篇讨论传感器、图像、视频、实例、语言和基础模型的揭示能力；第四篇要求所有结论回到公开协议与可复现评价。全书最重要的方法论不是某个模型，而是先定义任务和证据，再比较能力。

未来优先问题包括强伪装样本的难度标定、多视角与多模态数据、主动视角选择、基础模型的专域适配，以及人机协同评价。这些方向必须证明新增能力来自几何、时间、语义或主动观测，而不是只来自更大模型和更多数据。

两用治理不是附加免责声明。平台优先开放评价、数据治理、失败分析与防御工具；攻击性生成只公开足以理解和复核机制的最小细节，并根据可部署程度、现实目标和防御价值分级发布。

CamoGED 不宣称终结隐藏—揭示竞赛。它提供的是一套可继续修订的地图、工具和规则，使新的数据、模型和案例能够被比较、复算和审查。''',
    "将终章压缩为一次正式收束，删除第二轮展望和‘继续’式尾句",
)

# ---------------------------------------------------------------------------
# 4. Appendix: turn the short index into an actual publication apparatus
# ---------------------------------------------------------------------------

write(
    "book/chapters/appendix-resources.qmd",
    '''---
title: "附录：数据、指标、术语与出版说明"
subtitle: "Appendix: Datasets, Metrics, Terminology, and Publication Notes"
bibliography: ../references.bib
---

## A　数据集登记规范 {#sec-a}

书中数据集表由 `data/datasets.yaml` 生成。正式版本只展示已核验记录，每条至少包含：名称、任务、模态、规模、正式划分、标注粒度、论文或官方页面、许可证、发布状态、最后核验日期与备注。项目只提供导航和校验信息，不重新分发受限数据。

| 字段 | 最低要求 | 说明 |
|---|---|---|
| `name` / `task` | 必填 | 避免把图像、视频、实例、指代和多模态任务混排 |
| `split` | 必填 | 明确训练、验证、测试及是否仅测试 |
| `annotation` | 必填 | 二值 mask、实例、轨迹、语言、问答或信号标定 |
| `license` | 必填 | 不明时标为待核，不进入正式下载表 |
| `publication_status` | 必填 | 正式发表、预印本、项目发布或撤回 |
| `last_verified` | 必填 | 动态事实的最后核验日期 |
| `verified` | 必填 | 正式书稿只渲染 `true` |

第10章提供任务版图，网站 `/datasets` 提供动态导航；附录不复制可能迅速过期的完整排行榜。

## B　指标速查 {#sec-b}

| 层级 | 典型指标 | 方向 | 主要问题 | 不能替代什么 |
|---|---|:---:|---|---|
| 像素/前景图 | MAE、$F_\\beta^w$ | ↓ / ↑ | 整体误差、漏检与误报 | 结构、实例和时间 |
| 结构 | $S_\\alpha$、$E_\\phi$、Boundary IoU | ↑ | 形状、区域和边界 | 任务代价 |
| 实例 | AP、AR、Mask AP | ↑ | 是否分清多个目标 | ID 与轨迹 |
| 视频 | $\\mathcal J$、$\\mathcal F$、$\\mathcal J\\&\\mathcal F$ | ↑ | 区域与边界 | 时间稳定性；后者应另报 |
| 生成 | FID/KID、LPIPS、SSIM | ↓/↑ | 分布或感知真实性 | 伪装/攻击有效性 |
| 对抗 | ASR、AP drop、迁移率 | ↑ | 特定观察者是否被误导 | 人类自然性、物理鲁棒性 |
| 人因 | 反应时、hit/miss、$d'$ | 依定义 | 观察者敏感性与偏置 | 机器分割质量 |
| 物理信号 | 热对比、SCR、光谱角 | 依定义 | 特定传感器信号差异 | 跨传感器任务结果 |

指标首次出现必须注明实现、版本、阈值、方向和聚合方式。视频、物理和人因实验还应报告方差、置信区间或重复次数。

## C　统一报告模板 {#sec-c}

本书采用：

$$
\\mathcal E=\\langle O,X,T,P,M\\rangle,
$$

其中 $O$ 为观察者，$X$ 为输入/观测信道，$T$ 为任务，$P$ 为协议，$M$ 为指标集合。文本提示、人工框和交互次数属于任务输入或协议条件，不应被伪装成模型自动能力。

一个最小机器评测 manifest：

```yaml
name: cod-mask-example
observer: model-name-and-version
channel: RGB image
task: camouflaged object segmentation
protocol: fixed test split; automatic prediction; no manual prompt
metrics: [mae, fw, sm, em, boundary_iou]
implementation_version: camo-eval-x.y.z
uncertainty: bootstrap 95% CI
last_verified: 2026-07-13
```

## D　术语中英对照 {#sec-d}

- **hider / seeker / evaluator**：隐藏方／揭示方／评价者；跨域总称。
- **crypsis / concealment**：以降低察觉概率为目标的隐蔽。
- **masquerade**：目标被察觉但被当作无关对象的伪装性拟态。
- **mimicry**：信号或外观对另一模型对象的拟态，范围不等同于伪装。
- **disruptive coloration**：瓦解色；通过竞争边缘和轮廓破坏降低整体组织。
- **countershading**：消影；以体表明暗抵消部分形状阴影线索。
- **stealth / low observable**：隐身／低可探测；需说明具体信道和任务。
- **COD / VCOD / CIS**：伪装目标检测（社区通常指像素分割）／视频 COD／伪装实例分割。
- **adversarial camouflage**：针对机器观察者优化的对抗伪装；不自动等于对人隐蔽。

## E　检索、核验与证据等级 {#sec-e}

检索数据库、关键词、纳入标准与截止日期见 `docs/BOOK_SEARCH_METHODOLOGY.md`；逐项事实问题见 `docs/BOOK_FACTCHECK_REGISTER.md`。正文使用三类主要证据：P 级一手论文、标准与档案；S 级权威专著与综述；T 级预印本、项目页与临时资料。关键历史事实和“首个/最大”结论至少需要一条 P 级证据。

## F　代码、项目与动态资源 {#sec-f}

- 书稿源码：`book/`
- 数据元数据：`data/papers.yaml`、`data/datasets.yaml`、`data/leaderboard.yaml`
- 评价工具：`camo-eval/`
- 动态资源：网站 `/papers`、`/datasets`、`/leaderboard`、`/demo`
- 未发表作者项目：`projects/coder`、`projects/flowcamo`、`projects/dualvcod`

未发表项目在正文中只作为研究议程，不作为已完成原创贡献。动态网站可以展示开发状态，但正式书稿不得预填结果。

## G　图像版权与版本清单 {#sec-g}

正式发布前，每幅外部图像应登记：文件名、标题、作者/机构、原始链接、年份、许可、是否改绘、署名文字和核验日期。无法确认许可的历史图、艺术作品、军事照片和动物摄影不得直接进入发行版；优先使用公版、开放许可、作者授权或原创示意图。

本版版本日期：**2026-07-13**。引用元数据见仓库根目录 `CITATION.cff`；正文采用 CC BY 4.0，代码采用 Apache-2.0，数据集遵循各自上游许可。
''',
    "将简短资源索引扩充为数据、指标、报告、术语、核验、项目和版权出版附录",
)

# Compilation plan: synchronize title and turn the uniqueness claim into a bounded claim.
replace(
    "docs/BOOK_COMPILATION_PLAN.md",
    "## 《伪装：生成、识别与评价——自然、战争与机器的跨域综观》",
    "## 《伪装：生成、识别与评价——自然、战争与机器的跨域综观》\n\n> 文档状态：编纂计划，不作为事实来源。涉及“首个、唯一、最大”的定位结论，必须按 `BOOK_SEARCH_METHODOLOGY.md` 和 `BOOK_FACTCHECK_REGISTER.md` 核验后才能进入正式书稿。",
    "给编纂计划增加事实核验边界",
)
replace(
    "docs/BOOK_COMPILATION_PLAN.md",
    "**关键发现：没有任何一本书同时跨越四个学科领域，也没有任何一本同时覆盖生成、识别、评价三支柱。**",
    "**工作性发现：据当前检索，尚未发现同时系统覆盖四类视角并把生成、识别、评价作为同等支柱的同类专著；该结论须随版本更新检索范围与截止日期。**",
    "将绝对唯一性结论改为有检索边界的工作性判断",
)

# ---------------------------------------------------------------------------
# 5. Remove residual short-tail expansion in summary sections without touching body prose.
# ---------------------------------------------------------------------------

for rel in [
    "book/chapters/05-physical-generation.qmd",
    "book/chapters/07-digital-generation.qmd",
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "book/chapters/11-image-cod.qmd",
    "book/chapters/12-video-cod.qmd",
    "book/chapters/13-instance-extended.qmd",
    "book/chapters/15-unified-evaluation.qmd",
    "book/chapters/16-frontiers-ethics.qmd",
]:
    text = read(rel)
    # Remove runs of at least three very short standalone paragraphs immediately before further reading.
    pattern = r"(?m)(?:\n[^\n#]{1,24}\n){3,}(?=\n## 延伸阅读)"
    new, n = re.subn(pattern, "\n", text)
    if n:
        write(rel, new, f"清理延伸阅读前连续短句式扩写（命中 {n} 处）")

# Record the actual run.
write(
    "book/EDITORIAL_CHANGELOG.md",
    "# Editorial revision log\n\nRevision date: 2026-07-13\n\n" + "\n".join(CHANGELOG) + "\n",
    "记录本轮自动化编审涉及的全部文件和目的",
)

print("Applied editorial revision:")
for item in CHANGELOG:
    print(item)
