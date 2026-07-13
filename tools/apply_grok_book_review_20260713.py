#!/usr/bin/env python3
"""Apply the still-relevant Grok editorial findings to the active book branch."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CHAPTERS = BOOK / "chapters"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one match, found {count}: {old[:100]!r}")
    write(path, text.replace(old, new, 1))


CHAPTERS_META = [
    ("01-essence-and-the-game.qmd", "统一框架与术语", "定义隐藏—揭示博弈，并显式区分隐真、示假与功能评价。", "框架/术语", "全书"),
    ("02-natural-camouflage.qmd", "自然伪装", "从视觉生态、行为与观察者实验提炼跨域机制。", "自然/隐真", "第5、11、16、19章"),
    ("03-military-camouflage.qmd", "军事伪装", "梳理历史、工程信道与任务层级，限定效能证据。", "军事/隐真与示假", "第5、6、9、15章"),
    ("04-camouflage-in-art.qmd", "艺术与视觉文化", "讨论格式塔、观看方式与文化中的伪装表达。", "人文/示假", "第5、7、8章"),
    ("05-physical-generation.qmd", "物理生成", "把颜色、纹理、几何、材料与制造约束组织成生成问题。", "生成/隐真", "第6、15、16、20章"),
    ("06-physical-adversarial.qmd", "物理对抗伪装", "讨论机器观察者下的物理压力测试及多维评价边界。", "生成/对抗", "第9、15、20章"),
    ("07-digital-generation.qmd", "数字生成与信息隐藏", "区分隐藏真实信息、伪造表象与操纵数字证据。", "生成/隐真与示假", "第9、15、18章"),
    ("08-intelligent-generation.qmd", "智能生成", "梳理GAN、扩散、风格迁移与合成数据增强。", "生成/研究议程", "第10—16、20章"),
    ("09-physical-digital-detection.qmd", "物理与数字揭示", "从多信道证据、取证与融合角度组织揭示方。", "识别/揭示", "第10—18章"),
    ("10-intelligent-overview-datasets.qmd", "任务、协议与数据", "冻结任务、模态、监督和数据使用边界。", "识别/基础设施", "第11—20章"),
    ("11-image-cod.qmd", "图像COD", "按证据范围梳理单图伪装分割方法与失败模式。", "识别/轨道B", "第15、16、18章"),
    ("12-video-cod.qmd", "视频COD", "处理运动、记忆、时序传播与视频协议。", "识别/时序", "第17、18章"),
    ("13-instance-extended.qmd", "实例与扩展任务", "定义实例、bbox、指代、协同与开放词汇任务。", "识别/多轨道", "第17—19章"),
    ("14-foundation-models.qmd", "基础模型", "分析SAM、CLIP、DINO与MLLM的能力来源和协议成本。", "识别/基础模型", "第15、17、18章"),
    ("15-unified-evaluation.qmd", "评价的统一语言", "建立观察者—信道—任务—协议—指标五元组和三轨道。", "评价/总纲", "第16—20章"),
    ("16-detectability-curves.qmd", "退化响应", "定义R_ctrl、R_std、R_obs、dAUC与τ₅₀工作框架。", "评价/行为可检测性", "第20、21章"),
    ("17-temporal-cross-model.qmd", "时序与跨模型桥接", "处理T_FSD、删失、生存曲线和公共输出模式。", "评价/时序", "第18—20章"),
    ("18-reliability-calibration.qmd", "预测可靠性", "区分校准、不确定性、拒答和共形覆盖事件。", "评价/可靠性", "第20、21章"),
    ("19-cross-model-irt.qmd", "跨模型测量", "用一致性、IRT-A/B与DIF研究能力—难度和人机映射。", "评价/测量学", "第20、21章"),
    ("20-causal-standardization.qmd", "因果与标准化", "组织数字孪生、探索/确证、统计推断和复现治理。", "评价/因果与治理", "第21章与附录"),
    ("21-frontiers-ethics.qmd", "前沿与责任边界", "汇总3D/4D、主动观察、两用风险和开放治理。", "前沿/伦理", "持续回馈生成、识别与评价"),
]

MAPPING = {
    "01-essence-and-the-game.qmd": ("框架与术语；同时覆盖隐真、示假、揭示和评价。", "向后统摄第2—20章，并在第21章接受治理回看。", "跨域关系是有限结构类比，不是机制、效用和因果历史的完全同构。"),
    "02-natural-camouflage.qmd": ("自然域的隐真、拟态、行为选择和观察者依赖。", "向前依赖第1章术语；向后连接第5章生成、第11章识别、第16章退化响应和第19章人机测量。", "人类或机器观察者只能作为特定代理，不能替代真实捕食者与生态适应度。"),
    "03-military-camouflage.qmd": ("军事史与工程信道中的隐真、示假和目标获取。", "连接第5—6章生成、第9章多信道揭示和第15章任务化评价。", "历史案例、图案流行与现实任务效能必须分开；不从公开叙述推导现实部署结论。"),
    "04-camouflage-in-art.qmd": ("视觉文化中的示假、注意操纵和观看机制。", "为第5、7、8章提供形式与感知概念，并由第15、19章限定观察者效应。", "审美、文化解释和视觉错觉不能直接替代可检测性或任务效用。"),
    "05-physical-generation.qmd": ("物理域的生成与隐真设计。", "承接第2—4章机制，连接第6章对抗、第15—16章评价和第20章因果审计。", "相似度、自然度和可制造性是设计证据，不等于功能性伪装成功。"),
    "06-physical-adversarial.qmd": ("机器观察者下的物理对抗压力测试。", "连接第9章揭示、第15章多维评价和第20章因果/复现协议。", "仅讨论机制、评价和防御；不提供面向现实敏感系统的规避优化配方。"),
    "07-digital-generation.qmd": ("数字域中的隐真、示假、身份与信息操纵。", "连接第9章数字取证、第15章评价和第18章可靠性。", "隐藏信息、伪造内容和误导决策是不同任务，不能以单一视觉自然度概括。"),
    "08-intelligent-generation.qmd": ("学习式生成、合成增强与作者研究议程。", "向后服务第10—14章识别，并由第15—16、20章评价其真实收益。", "生成样本进入正文前须有真实测试集收益、标注一致性和污染审计；作者项目不作既成方法。"),
    "09-physical-digital-detection.qmd": ("揭示方的多信道证据与数字取证。", "为第10—14章任务与模型提供信道基础，并由第15、18章评价融合与可靠性。", "增加信道不自动保证效能；标定、配准、代价和故障模式属于协议。"),
    "10-intelligent-overview-datasets.qmd": ("智能识别的任务、数据、监督和协议基础设施。", "向后支撑第11—14章方法和第15—20章评价。", "Catalog中的metadata-only、预印本或许可未知条目不自动成为正式事实表证据。"),
    "11-image-cod.qmd": ("轨道B的图像像素级识别。", "承接第10章协议，连接第15章指标、第16章退化响应和第18章可靠性。", "标准指标与教学代理严格分开；总体均值不能替代失败分层和外部测试。"),
    "12-video-cod.qmd": ("视频中的运动、记忆和持续识别。", "承接第11章单图证据，连接第17章事件时间和第18章不确定性。", "J/F/J&F只描述区域/边界；持续发现、闪烁、删失和重捕获另报。"),
    "13-instance-extended.qmd": ("实例、bbox、指代、协同与开放词汇扩展。", "连接第17章公共输出、第18章可靠性和第19章跨模型测量。", "不同任务只共享记录格式和可桥接响应，不构造未经验证的跨轨总分。"),
    "14-foundation-models.qmd": ("基础模型能力、提示协议和系统成本。", "承接第10—13章任务，连接第15、17、18章的协议、桥接和可靠性。", "人工提示、外部检测器、额外数据、版本和服务更新必须显式记录。"),
    "15-unified-evaluation.qmd": ("第四篇总纲：统一报告语言而非统一总分。", "汇总第1—14章输出，向后分派到第16—20章。", "观察者、信道、任务和协议改变时，指标数值不能直接混排。"),
    "16-detectability-curves.qmd": ("行为可检测性的退化响应测量。", "承接第15章对象级响应，连接第20章确证设计和第21章实证前沿。", "R_ctrl/R_std、主dAUC和τ₅₀是CamoGED工作定义，依赖T_j、区间和参考分布。"),
    "17-temporal-cross-model.qmd": ("视频事件时间和跨模型行为桥接。", "承接第12、13、15章，连接第18、19、20章。", "未检出按删失处理；二元黑箱不能伪装为可匹配工作点系统。"),
    "18-reliability-calibration.qmd": ("置信度、拒答、校准和共形保证。", "承接第15、17章行为输出，连接第20章确证与第21章治理。", "条件于匹配的框覆盖不等于端到端发现保证；黑箱重复不自动等于认知不确定性。"),
    "19-cross-model-irt.qmd": ("行为一致性、能力—难度和人机映射。", "承接第15—18章响应，连接第20章统计设计和第21章开放问题。", "IRT难度依赖面板、任务和工作点；测量不变性不成立时不强行共量尺。"),
    "20-causal-standardization.qmd": ("因果归因、探索/确证和标准化基础设施。", "汇合生成、识别和第15—19章，向第21章治理与附录模板输出。", "数字孪生结论先属于支持域；工具和统计模型不能替代识别假设与外部复核。"),
    "21-frontiers-ethics.qmd": ("前沿、伦理、两用边界和开放治理。", "回看前20章，并把未证实问题反馈到生成、识别和评价路线。", "前瞻性判断必须标明假设和证据缺口；不把研究议程写成已完成能力。"),
}


def mapping_block(position: str, links: str, boundary: str) -> str:
    return (
        "::: {.callout-note collapse=\"true\"}\n"
        "## 本章与全书映射\n\n"
        f"- **本章定位**：{position}\n"
        f"- **前后依赖**：{links}\n"
        f"- **证据与风险边界**：{boundary}\n"
        ":::\n\n"
    )


# 1. Full navigation and interdependence map in the preface.
index = BOOK / "index.qmd"
text = read(index)
if "## 全书导航与依赖关系" not in text:
    rows = ["| 章 | 标题 | 一句话摘要 | 主类型 | 主要接口 |", "|---:|---|---|---|---|"]
    for i, (_, title, summary, kind, interface) in enumerate(CHAPTERS_META, start=1):
        rows.append(f"| {i} | {title} | {summary} | {kind} | {interface} |")
    nav = """
## 全书导航与依赖关系 {.unnumbered}

本书不是按互不相干的主题并列，而是按“机制与历史 → 生成 → 识别 → 评价 → 前沿与治理”递进。生成与识别共同向评价提供对象、响应和失败样本；评价又把新的难例、证据缺口和治理要求反馈给生成与识别。

```{mermaid}
flowchart LR
  P1["第一篇：机制、历史与文化<br/>Ch1–4"] --> P2["第二篇：生成<br/>Ch5–8"]
  P1 --> P3["第三篇：识别<br/>Ch9–14"]
  P2 --> P4["第四篇：评价<br/>Ch15–20"]
  P3 --> P4
  P4 --> P5["第五篇：前沿与治理<br/>Ch21"]
  P5 -. 证据缺口与风险反馈 .-> P2
  P5 -. 新任务与协议反馈 .-> P3
```

""" + "\n".join(rows) + "\n\n"
    marker = "## 证据与版本约定 {.unnumbered}\n"
    if marker not in text:
        raise RuntimeError("book/index.qmd: evidence marker not found")
    text = text.replace(marker, nav + marker, 1)
    write(index, text)


# 2. Explicit conceal-the-real / present-the-false framework in Chapter 1.
ch1 = CHAPTERS / "01-essence-and-the-game.qmd"
text = read(ch1)
if "### 1.3.1 隐真与示假" not in text:
    insert = r'''
### 1.3.1 隐真与示假：设计手段不等于功能效果 {#sec-conceal-deceive}

为了贯通自然、军事、艺术和人工智能，本书再增加一条功能区分：

- **隐真（concealing the real）**：压低真实目标、状态或信息进入观察者决策链的证据，使其更难被察觉、定位或识别；
- **示假（presenting the false）**：向观察者提供替代类别、虚假状态、假目标或错误因果解释，使其即使接收到信号也作出错误判断。

背景匹配、低可探测设计和信息隐藏主要偏向隐真；拟态、假目标、深度伪造和部分对抗样本主要偏向示假；瓦解色、运动眩惑和对抗迷彩则可能同时压低真实证据并制造竞争线索。两条路径可以组合，但评价事件不同：隐真首先看命中、漏报和首次发现，示假还要看误分类、错误指代、虚假解释和负样本幻觉。

::: {.callout-important}
## “像背景”不是“更难发现”的充分条件

目标—背景相似度属于设计手段或代理描述量，可检测性属于观察者在特定信道、任务和协议下的功能结果。一般不能推出：

$$
\Delta\operatorname{Sim}(\text{target},\text{background})>0
\;\Longrightarrow\;
\Delta P_{\mathrm{det}}<0.
$$

轮廓、运动、热特征、语义先验或观察策略都可能使相似度提高而发现概率不降。反之，眩惑图案甚至可能更醒目，却降低方向估计或任务命中率。因而，设计量必须与第15—20章的行为响应、可靠性和任务效用成对报告。
:::

| 功能路径 | 主要改变 | 典型问题 | 主评价入口 |
|---|---|---|---|
| 隐真 | 真实证据强度或可分性 | 是否更晚、更少被发现 | 第15—18章 |
| 示假 | 类别、状态或因果解释 | 是否被误认、误指或产生幻觉 | 第15、17—19章 |
| 隐真 + 示假 | 同时压低真线索并制造竞争线索 | 是否在多观察者、多信道下仍成立 | 第16、20章 |

'''
    marker = "::: {.callout-note}\n## 一处历史争议：Thayer 的消影定律"
    if marker not in text:
        raise RuntimeError("chapter 1 historical callout marker not found")
    text = text.replace(marker, insert + marker, 1)
    write(ch1, text)


# 3. Chapter-end mapping cards.
for filename, _title, _summary, _kind, _interface in CHAPTERS_META:
    path = CHAPTERS / filename
    text = read(path)
    if "## 本章与全书映射" in text:
        continue
    block = mapping_block(*MAPPING[filename])
    marker = "## 延伸阅读"
    if marker in text:
        text = text.replace(marker, block + marker, 1)
    else:
        text = text.rstrip() + "\n\n" + block
    write(path, text)


# 4. Protocol manifest extension, environment freeze, pollution and budget fields.
appendix = CHAPTERS / "appendix-resources.qmd"
text = read(appendix)
if "dataset_hashes:" not in text:
    old = """implementation_version: camo-eval-x.y.z
threshold_policy: continuous maps for COD core; declared threshold for binary set metrics
statistical_unit: image/object
uncertainty: scene-cluster bootstrap 95% CI
last_verified: 2026-07-13
"""
    new = """implementation_version: camo-eval-x.y.z
threshold_policy: continuous maps for COD core; declared threshold for binary set metrics
statistical_unit: image/object
uncertainty: scene-cluster bootstrap 95% CI
dataset_hashes: [sha256:...]
prediction_hashes: [sha256:...]
environment_lock: requirements-lock.txt
container_image_digest: sha256:...
pollution_audit:
  status: unknown
  model_knowledge_cutoff: unverified
  private_holdout: true
query_budget:
  provider: null
  max_calls: null
  max_cost: null
last_verified: 2026-07-13
"""
    if old not in text:
        raise RuntimeError("appendix base manifest block not found")
    text = text.replace(old, new, 1)

if "- **concealing the real / presenting the false**" not in text:
    marker = "- **behavioral detectability**：行为可检测性；给定协议下任务成功概率。"
    addition = (
        "- **concealing the real / presenting the false**：隐真／示假；前者压低真实证据，后者制造替代解释或虚假证据。\n"
        + marker
    )
    if marker not in text:
        raise RuntimeError("appendix glossary marker not found")
    text = text.replace(marker, addition, 1)

if "完整的协议扩展字段" not in text:
    marker = "退化响应实验还应加入："
    replacement = (
        "完整的协议扩展字段、哈希、环境冻结、污染审计和查询预算见 "
        "`docs/EVALUATION_MANIFEST_EXTENSION_V1.md`。\n\n" + marker
    )
    if marker not in text:
        raise RuntimeError("appendix degradation manifest marker not found")
    text = text.replace(marker, replacement, 1)
write(appendix, text)


# 5. New research-agenda / ethics / data-card appendix.
agenda = CHAPTERS / "appendix-research-agenda.qmd"
write(
    agenda,
    r'''---
title: "附录：开放问题、研究议程与模板"
subtitle: "Open Questions, Ethics Protocol, and Data Card Templates"
bibliography:
  - ../references.bib
  - ../evaluation-references.bib
---

## H　六项开放科学问题 {#sec-h}

以下问题是第15—21章的研究议程，不是已完成结论。

| 编号 | 核心问题 | 最小证据 | 主要章节 |
|---|---|---|---|
| SQ1 | 如何建立跨尺度、遮挡、相似度和成像条件稳定的行为可检测性量尺？ | 独立确证集、R_std、dAUC、τ₅₀与敏感性分析 | 第16、20章 |
| SQ2 | 检测器、分割器、跟踪器与VLM能在多大程度上共享公共行为坐标？ | 冻结匹配规则、原生/匹配工作点、正负样本响应 | 第15、17章 |
| SQ3 | 视频中的“发现”应如何处理持续性、删失、丢失和重捕获？ | T_FSD、生存曲线、序列级重采样 | 第17章 |
| SQ4 | 校准、拒答与共形覆盖在分布漂移和漏检条件下是否仍可靠？ | 覆盖事件、分母、区间效率、漂移分层 | 第18章 |
| SQ5 | 数字孪生和真实编辑能否识别退化因素的因果效应？ | 随机干预、操纵检查、安慰剂和真实域复核 | 第20章 |
| SQ6 | 人类、动物与机器何时可以共量尺，何时必须保持多尺度？ | 共同锚定、等价任务、DIF和链接误差 | 第19、21章 |

## I　人类观察者实验伦理与预注册模板 {#sec-i}

```yaml
study_id: human-detectability-study-v1
research_question: null
ethics_approval:
  institution: null
  protocol_number: null
  status: pending
participants:
  target_n: null
  inclusion: null
  exclusion: null
  compensation: null
  vulnerable_population: false
stimuli:
  source_and_license: null
  sensitive_content_screening: null
  target_present_ratio: null
  randomization: null
observer_conditions:
  display: null
  viewing_distance: null
  luminance_and_calibration: null
  exposure_time: null
tasks: [presence, localization, identification]
responses: [hit, miss, false_alarm, correct_rejection, reaction_time, click_location]
primary_hypotheses: []
sequential_rule: none
exclusions_and_missingness: preregistered
privacy:
  raw_video_or_eye_tracking: restricted
  retention_period: null
  deidentification: null
analysis:
  statistical_unit: participant_and_stimulus
  model: hierarchical
  multiplicity: null
  sesoi: null
```

伦理审批不能被模板替代。涉及敏感场景、未成年人、眼动/生理信号或可识别影像时，应追加机构审查、最小化采集和访问控制。

## J　数据卡模板 {#sec-j}

```yaml
dataset_id: null
version: null
purpose_and_tasks: []
modalities: []
collection:
  dates: null
  geography: null
  devices: []
  sampling_frame: null
subjects_and_targets:
  categories: []
  sensitive_attributes: []
annotations:
  types: []
  annotator_protocol: null
  uncertainty_or_ignore_regions: null
splits:
  grouping_unit: scene_sequence_subject_source
  train: null
  calibration: null
  validation: null
  test: null
deduplication:
  exact_hash: null
  perceptual_hash: null
  source_level: null
licenses_and_rights:
  upstream_license: null
  redistribution_allowed: false
  restrictions: []
pollution_audit:
  public_since: null
  known_model_exposure: unknown
  private_holdout: null
quality:
  missingness: null
  known_biases: []
  known_label_issues: []
provenance:
  manifest_hash: null
  files_hashes: []
last_verified: null
verified_by: null
```

## K　开放问题进入正文的准入规则 {#sec-k}

1. 研究问题可以进入本附录，但不能以未来时架构或预填性能进入方法谱系表；
2. 作者项目只有在代码、权重、预测、协议和独立复核齐备后，才从研究议程升级为正式方法；
3. 人因和因果结论在伦理、功效、操纵检查和确证设计完成前保持假设状态；
4. 动态Catalog负责发现候选，正文只引用经过一手来源和适用范围核验的工作；
5. 每次正式发布对SQ1—SQ6给出状态：未启动、探索、确证中、部分支持、被推翻或已稳定复现。
''',
)


# 6. Add appendix to Quarto structure.
quarto = BOOK / "_quarto.yml"
text = read(quarto)
entry = "    - chapters/appendix-research-agenda.qmd\n"
if entry not in text:
    marker = "  appendices:\n    - chapters/appendix-resources.qmd\n"
    if marker not in text:
        raise RuntimeError("_quarto.yml appendices marker not found")
    text = text.replace(marker, marker + entry, 1)
    write(quarto, text)


# 7. Detailed manifest extension and reproducible environment guide.
manifest_doc = ROOT / "docs/EVALUATION_MANIFEST_EXTENSION_V1.md"
write(
    manifest_doc,
    '''# 评价协议 Manifest 扩展 v1.0

状态：`PROTOCOL-DRAFT`。这些字段面向第16—20章的退化、可靠性、黑箱和污染审计；并不表示 `camo-eval` 核心API已经实现全部字段。

## 最小扩展

```yaml
protocol_id: detectability-eval-v1
implementation_version: null
dataset_version: null
dataset_hashes: []
prediction_revision: null
prediction_hashes: []
environment:
  python: null
  os: null
  dependency_lock: null
  container_image: null
  container_digest: null
severity_factors:
  target_scale:
    raw_symbol: a
    raw_measure: sqrt_pixel_area
    transform_id: log_scale_decreasing_v1
    transform_parameters: {}
    scan_range: []
    direction: higher_z_is_more_degraded
reference_distribution:
  id: P_star_v1
  source_manifest_hash: null
  weighting: uniform_or_registered
responses:
  positive: Y_plus
  negative_correct_rejection: Y_minus
  false_positive_count: N_FP
operating_points:
  native: true
  matched_false_alarm: null
uncertainty:
  method: scene_cluster_bootstrap
  confidence_level: 0.95
pollution_audit:
  model_knowledge_cutoff: unknown
  dataset_publication_date: null
  known_overlap: unknown
  private_holdout: false
query_budget:
  provider: null
  model_version: null
  max_calls: null
  max_cost: null
  retry_policy: null
```

## 哈希与可重建性

- 数据清单、划分、预测和协议文件分别计算SHA-256；
- 记录依赖锁文件和容器镜像digest；
- API模型保存请求日期、模型版本、prompt和原始响应；
- 不把浮动标签的容器镜像视为冻结环境；
- 报告可从原始响应重新生成，而不是只保存最终表格。

## 环境冻结建议

优先级从高到低：

1. 容器镜像digest + 依赖锁文件；
2. Conda/uv/pip-tools锁文件 + OS/驱动信息；
3. 仅`requirements.txt`，但必须固定直接和传递依赖版本；
4. 只写软件名称不满足正式复现要求。

Docker示例只说明冻结方式，不保证所有GPU/传感器实验可在容器内完整复现：

```dockerfile
FROM python:3.11-slim@sha256:<digest>
COPY requirements-lock.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-lock.txt
WORKDIR /workspace
COPY . /workspace
```

## 污染和预算

污染审计记录“已知、疑似、未知、低风险、私有隔离”状态；无法核实模型截止日期时保持`unknown`。查询预算是协议的一部分，任何预算变更若改变模型、prompt、重复数或抽样设计，都需要新的protocol revision。
''',
)

human_template = ROOT / "docs/templates/HUMAN_OBSERVER_PROTOCOL_TEMPLATE.md"
write(human_template, "# 人类观察者实验模板\n\n完整字段见书稿附录 I。使用前必须取得适用的伦理审批，并补充机构、被试、刺激、显示条件、隐私、统计和退出规则。\n")
data_template = ROOT / "docs/templates/DATA_CARD_TEMPLATE.md"
write(data_template, "# CamoGED Data Card 模板\n\n完整字段见书稿附录 J。至少记录任务、模态、采集、标注、分区、去重、许可、污染、质量、哈希和最后核验日期。\n")


# 8. Review response register.
response = ROOT / "docs/GROK_BOOK_REVIEW_RESPONSE_20260713.md"
write(
    response,
    '''# Grok 专著审查意见处理记录（2026-07-13）

## 已在评价篇重构中覆盖

- 第15—20章已经系统纳入对象级正负响应、原生/匹配误报工作点、黑箱VLM协议、T_FSD、生存分析、UQ、校准、共形预测、dAUC、τ₅₀、IRT-A/B、DIF、数字孪生、探索/确证、SESOI与bootstrap。
- 第20章和附录已经区分标准实现、实验性描述量和外部实验协议，并纳入许可、污染和私有隔离集。

## 本轮新增

- 前言新增21章完整摘要导航和篇章依赖图；
- 第1章新增“隐真/示假”显式框架，并明确相似度不推出可检测性下降；
- 第1—21章统一增加“本章与全书映射”框，包含定位、依赖和证据/风险边界；
- 附录manifest增加哈希、环境锁、容器digest、污染审计和查询预算；
- 新增评价manifest扩展与环境冻结指南；
- 新增SQ1—SQ6开放问题、人因伦理模板和data card模板。

## 暂不在本轮扩写

- 生物和军事章节已有观察者评价流程、视觉搜索、人造猎物、D/O/R/I、TOD/TTP和多信道卡片；本轮以映射框和评价接口强化，不再无证据增加定量数字。
- CV/ML章节的代码迁移到独立附录属于全书版式二校，需结合PDF分页和代码溢出统一处理，避免只移动个别代码块破坏叙事。
- 图像配色、印刷规范和版权清单仍属于正式出版QA。

## 仍需外部复核

- 评价专项书目DOI/版本终核；
- 统计、测量学、共形、生存分析和因果推断同行评审；
- 生物、军事史/传感器与版权领域审校；
- PDF中文字体、公式、宽表、代码和图像分辨率校样。
''',
)

print("Grok book review remediation applied")
