# CamoGED `data/` 模式规范（冻结接口）

> **schema_version: 1.0**
>
> `data/` 是本项目的**单一事实来源（single source of truth）**：Awesome 列表（`awesome/README.md`）与后续网站（`web/`）均由它生成，专著的数据集表（第10章）与附录 A 也据它核对。
>
> 本文件是 §0.2 的**冻结接口契约之一**。字段名一经冻结不得擅改；任何变更须走 `interface-change` 流程（见 `docs/CONTRIBUTOR_WORK_PACKAGES.md` §0.3），并同步更新本文件的 `schema_version` 与受影响的书稿/脚本。

---

## 0. 通用约定

- 三个文件：`data/papers.yaml`、`data/datasets.yaml`、`data/leaderboard.yaml`，各以一个顶层键（`papers:` / `datasets:` / `leaderboard:`）承载条目列表。
- 编码 UTF-8；缩进 2 空格；字符串用双引号。
- `*` 标注的字段为**必填**。未知/未核实的值一律写 `null`，**禁止猜测或杜撰**。
- **`id` 全局唯一**，命名用小写字母、数字与连字符；论文/方法的 `id` 建议与 `bibtex_key` 同名（见 §4）。
- 校验由 `scripts/check_data.py` 执行（见 §5），并在 CI 中作为门禁。

---

## 1. `papers.yaml` — 论文 / 方法登记

| 字段 | 类型 | 必填 | 取值/约束 | 说明 |
|------|------|:----:|-----------|------|
| `id` | str | * | 唯一、kebab-case | 建议等于 `bibtex_key` |
| `title` | str | * | | 论文/方法标题 |
| `authors` | str \| list[str] | * | | 作者；可 "Xiao et al." 或列表 |
| `venue` | str | * | 如 CVPR/TPAMI/CAAI AIR | 发表场所 |
| `year` | int | * | 1850–本年 | |
| `pillar` | str | * | `generation` \| `detection` \| `evaluation` | 三支柱（见 §3） |
| `domain` | str | * | `physical` \| `digital` \| `intelligent` | 三技术域 |
| `perspective` | str | * | `nature` \| `war` \| `art` \| `ai` | 三视角（biology 归 nature） |
| `task` | str | * | 见 §3 受控词表 | 主任务标签 |
| `paper` | str(url) | * | http(s) 且可访问 | 论文链接（DOI/arXiv 优先） |
| `code` | str(url) \| null |  | | 代码仓库 |
| `datasets` | list[str] |  | 元素须是 `datasets.yaml` 的 `id`/`name` | 使用/提出的数据集 |
| `bibtex_key` | str \| null |  | 与 `book/references.bib` 对齐 | 见 §4（告警级校验） |
| `notes` | str \| null |  | | 备注 |

```yaml
papers:
  - id: fan2020sinet
    title: "Camouflaged Object Detection"
    authors: ["Fan D-P", "Ji G-P", "Sun G", "Cheng M-M", "Shen J", "Shao L"]
    venue: "CVPR"
    year: 2020
    pillar: detection
    domain: intelligent
    perspective: ai
    task: image-cod
    paper: "https://openaccess.thecvf.com/content_CVPR_2020/html/Fan_Camouflaged_Object_Detection_CVPR_2020_paper.html"
    code: "https://github.com/DengPingFan/SINet"
    datasets: ["cod10k", "camo"]
    bibtex_key: fan2020sinet
    notes: "Defines the COD task; search-identification framework."
```

---

## 2. `datasets.yaml` — 数据集登记

| 字段 | 类型 | 必填 | 取值/约束 | 说明 |
|------|------|:----:|-----------|------|
| `id` | str | * | 唯一、kebab-case | 如 `cod10k` |
| `name` | str | * | | 展示名，如 `COD10K` |
| `task` | str | * | 见 §3 受控词表 | |
| `modality` | str | * | `rgb` \| `video` \| `multispectral` \| `multimodal` \| `thermal` \| `polarization` \| `depth` | 传感信道 |
| `size` | str \| null |  | 如 "5,066 camouflaged" | 规模（保留原文表述） |
| `split` | str \| null |  | 如 "3,040 train / 2,026 test" | 划分 |
| `year` | int \| null |  | | |
| `link` | str(url) \| null |  | 可访问 | 主页/下载页 |
| `license` | str \| null |  | | 许可证（**只链接不再分发**数据） |
| `bibtex_key` | str \| null |  | 与 `references.bib` 对齐 | |
| `notes` | str \| null |  | | |

```yaml
datasets:
  - id: cod10k
    name: "COD10K"
    task: image-cod
    modality: rgb
    size: "5,066 camouflaged (~10K total)"
    split: "3,040 train / 2,026 test; 78 sub-classes"
    year: 2020
    link: null
    license: null
    bibtex_key: fan2020sinet
    notes: "Largest image COD benchmark."
```

---

## 3. 受控词表（枚举）

修改/扩充任一词表都属 `interface-change`，须更新本节并通知专著作者（影响第1章 @tbl-matrix、第10章数据集表）。

- **pillar**：`generation` · `detection` · `evaluation`
- **domain**：`physical` · `digital` · `intelligent`
- **perspective**：`nature` · `war` · `art` · `ai`
- **modality**：`rgb` · `video` · `multispectral` · `multimodal` · `thermal` · `polarization` · `depth`
- **task**（初始集，可经流程追加）：
  `image-cod` · `video-cod` · `instance-cod` · `referring-cod` · `collaborative-cod` ·
  `open-vocab-cos` · `survey` · `generation` · `physical-adversarial` · `digital-adversarial` ·
  `foundation-model` · `dataset` · `application`
- **leaderboard.status**：`reported`（原文报告） · `reproduced`（本平台复现）

---

## 4. `leaderboard.yaml` — 排行榜（最高合规要求）

| 字段 | 类型 | 必填 | 取值/约束 | 说明 |
|------|------|:----:|-----------|------|
| `method` | str | * | | 方法名；本平台方法注明 "(ours)" |
| `dataset` | str | * | `datasets.yaml` 的 `id`/`name` | |
| `task` | str | * | §3 受控词表 | |
| `metrics` | map | * | 键见下；值为 float 或 `null` | **未核实一律 null** |
| `params_M` | float \| null |  | 单位百万 | 模型参数量 |
| `status` | str | * | `reported` \| `reproduced` | 数据来源类型 |
| `source` | str | * | url 或仓库内路径（如 `projects/coder`） | 可溯源 |
| `verified` | bool | * | 默认 `false` | 维护者已比对 source 后置 `true` |
| `protocol` | str \| null |  | 如 "COD10K+CAMO train" | 训练协议 |
| `notes` | str \| null |  | | |

**metrics 允许键**：检测 `Sm`（↑）、`Fw`（加权F，↑）、`Em`（↑）、`MAE`（↓）、`maxF`、`meanF`；实例 `AP`、`AR`；视频 `JF`（J&F）、`temporal`。键名须与 `camo-eval` 输出及第15章一致。

**零杜撰铁律**：任何**非 null** 的 metric 必须满足 `verified: true` 且 `source` 可解析；否则 CI 失败。`status: reported` 表示数字抄自原文，仍须经维护者**比对原文核实**后方可 `verified: true`。

```yaml
leaderboard:
  - method: "ZoomNeXt"
    dataset: "cod10k"
    task: image-cod
    metrics: { Sm: null, Fw: null, Em: null, MAE: null }   # 待从 TPAMI 2024 核实
    params_M: null
    status: reported
    source: "https://doi.org/10.1109/TPAMI.2024.3417329"
    verified: false
    protocol: "COD10K+CAMO train"

  - method: "coder (ours)"
    dataset: "cod10k"
    task: image-cod
    metrics: { Sm: null, Fw: null, Em: null, MAE: null }   # 待本平台复现
    params_M: null
    status: reproduced
    source: "projects/coder"
    verified: false
    protocol: "COD10K+CAMO train"
```

---

## 5. `bibtex_key` 与 `references.bib` 的契约

- `papers.yaml`/`datasets.yaml` 的 `bibtex_key` 应与 `book/references.bib` 中的键**同名同义**，使专著与列表共享同一引用身份。
- `references.bib` 由专著作者拥有（见 CODEOWNERS）。协作者需要新键时，在 PR 描述或 `interface-change` Issue 中提出，由作者并入。
- CI 的一致性检查为**告警级（不阻断）**：报告"data 中存在、references.bib 中缺失"的键，以及反向情况，便于双方对齐而不互相阻塞。

---

## 6. 校验规则（`scripts/check_data.py`，CI 门禁）

`check_data.py` 必须校验并在不满足时**非零退出**：

1. **结构**：三文件可解析；顶层键正确；每条含全部必填字段。
2. **枚举合法**：`pillar/domain/perspective/modality/task/status` 取值在 §3 内。
3. **唯一性**：`papers`/`datasets` 的 `id` 全局唯一、kebab-case；无重复。
4. **引用完整性**：`papers.datasets[]`、`leaderboard.dataset` 指向存在的 `datasets` 条目。
5. **链接非空可形**：`paper`/`link` 为 http(s)（连通性由 `check-links` 工作流另测）。
6. **零杜撰**：`leaderboard` 中任何非 null metric ⇒ `verified:true` 且 `source` 可解析；metric 键在允许集内。
7. **同源一致**：`awesome/README.md` 等于 `scripts/build_awesome.py` 的当前输出（`git diff` 为空）。
8. **告警**：`bibtex_key` 与 `references.bib` 的差异（仅打印，不失败）。

---

## 7. 消费方（只读）

- `scripts/build_awesome.py` → `awesome/README.md`（按 pillar × domain + perspective 分类）。
- 后续 `web/`（VitePress）→ `/papers`、`/datasets`、`/leaderboard`（**仅展示 `verified:true`**）、`/demo`。
- 专著（只读核对）：第1章 @tbl-matrix、第10章 @tbl-datasets、附录 A/D。

---

## 8. 现状与本模式的差异（B1 待对齐清单）

当前 `data/*.yaml` 与本模式存在如下差异，B1 任务负责对齐（属内部对齐，非接口变更）：

- `papers.yaml`：缺 `id`、`perspective`、`bibtex_key`；现用 `paper` 字段保留即可（本模式已采纳）。
- `datasets.yaml`：缺 `id`、`year`、`license`、`bibtex_key`；`modality` 现值 `rgb` 合规。
- `leaderboard.yaml`：已有 `status`/`source`；需**新增 `verified` 字段**（默认 `false`），并把 `dataset` 改为引用 `datasets.id`。

**受控词表的现存越界值与建议映射**（`scripts/check_data.py` 会逐条报出，按下表改）：

| 现值（字段） | 应改为 |
|--------------|--------|
| `military-cod` (task) | `image-cod`（"军事"写进 `notes` 或由 `perspective: war` 承载） |
| `multispectral-cod` (task) | `image-cod`（多光谱由 `modality: multispectral` 承载） |
| `multimodal` (task) | `image-cod` 或 `dataset`（多模态由 `modality: multimodal` 承载） |
| `adversarial` (task) | `physical-adversarial` 或 `digital-adversarial` |
| `cross-domain` (task) | `application` |
| `rgb-video` (modality) | `video`（"视频"由 `task: video-cod` 承载） |

> 对齐完成后，运行 `python scripts/check_data.py` 应全绿，`schema_version` 维持 1.0。运行 `python scripts/check_api.py` 则随 WP-A 各指标实现而逐步转绿。
