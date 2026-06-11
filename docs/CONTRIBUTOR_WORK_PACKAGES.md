# CamoGED 协作分工与工作包计划（给帮手）

> 目的：把与专著**界面清晰、相对独立**的工作（评测工具包、Awesome 列表与数据流水线）打包交付协作者，使其可与专著写作**并行推进、互不阻塞**。
> 本文件是可执行的工作说明，含任务分解、接口契约与**审计/验收要求**。建议置于仓库 `docs/CONTRIBUTOR_WORK_PACKAGES.md`。
>
> **协作者 = Codex 编码代理**，在维护者本机运行、以维护者身份（`@MichaelCSHN`）提交。因此边界**不靠 GitHub 身份强制**，而靠：① 代理遵守 `AGENTS.md`；② 与身份无关的 **CI 门禁**（`check_data.py`/`check_api.py`/链接/构建 diff）；③ 维护者推送前的 **diff 复核**。文中凡提"协作者/PR 评审/双方会签"，在本项目中即按上述三机制理解。

---

## 0. 总则：界面清晰、相对独立

### 0.1 目录所有权（硬边界）

> **分工调整（2026-06，取代最初分工）**：项目改为双代理协作——
> **Claude = 项目主管**，统揽全局并独占开发 `camo-eval/` 评测工具包及其 demo 面（HF Space、notebooks）；
> **Codex = 专著作者 + Awesome 模块**，负责 `book/` 写作/配图/审校与 `awesome/`+`data/` 流水线。
> 下表以此为准；最初"协作者改 camo-eval、专著作者写 book"的分工**已废止**。

| 区域 | 所有者 | Codex 可否改 |
|------|--------|--------------|
| `book/`（章节 `.qmd`、`references.bib`、`figures/`） | **Codex（专著作者）** | **是**（写作/配图/审校） |
| `awesome/` | **Codex** | 是 |
| `data/`（`papers/datasets/leaderboard.yaml`） | **Codex** | 是 |
| `scripts/build_awesome.py`、`scripts/check_data.py` | **Codex** | 是 |
| `web/`（数据驱动页面：papers/datasets/leaderboard/models） | **Codex** | 是（除 `web/hf-space/`） |
| `camo-eval/`（含 `tests/`、`notebooks/`） | **Claude（主管）** | **否**（只读消费 API） |
| `scripts/check_api.py`（camo-eval API 门禁） | **Claude** | **否** |
| `web/hf-space/`（camo-eval 演示） | **Claude** | **否** |
| `.github/workflows/`（CI） | 共同（分文件） | 是（仅其负责的工作流） |
| `AGENTS.md`、本文件、`docs/CODEX_DIRECTIVE.md` | **Claude（主管维护）** | 否 |
| 根级 `README.md`、`LICENSE`、`CITATION.cff` | 维护者 | 经评审 |

**原则**：Codex **不编辑 `camo-eval/`、`scripts/check_api.py`、`web/hf-space/`**；camo-eval 只通过下面冻结契约把产出（指标值）供 Codex 在排行榜/网站/专著中消费。需要 camo-eval 改动时写入 `NOTES_FOR_MAINTAINER.md`，由 Claude 处理。

### 0.2 三个冻结接口契约（两侧唯一的耦合点）

1. **`data/*.yaml` 模式**（见 §2.2）——专著的数据集表（第10章）、附录 A 与（后续）网站都从它生成；协作者负责填充与维护，模式一旦冻结不得擅改字段名。
2. **`camo-eval` 公开 API 名称与签名**（见 §1.2）——由第15章正文与**附录 B** 锁定；协作者按此实现，名称/签名不得更改（变更须走"接口变更"流程，见 §0.3）。
3. **引用键命名空间**——`data/papers.yaml` 与 `data/datasets.yaml` 中的 `bibtex_key`，应与 `book/references.bib` 的键**同名同义**。`references.bib` 由专著作者拥有；协作者若需新增键，在 PR 描述或专门 Issue 中提出，由作者并入；CI 仅做**告警级**一致性检查（不阻断），避免双方在同一文件上产生编辑冲突。

> 这三个契约就是"界面"。只要它们稳定，协作者改 `camo-eval/` 或 `data/` 永远不会碰坏专著，反之亦然。

### 0.3 协作流程（单一身份 / 本地代理）

- **分支（可选）**：建议每个子任务一条特性分支（如 `wp-a/s-measure`），便于 diff 复核；但由于代理以维护者身份本地提交，PR 评审不是身份强制，而是维护者**自审 + CI 门禁**。
- **边界执行**：由 `AGENTS.md`（代理行为规则）+ §5.2 CI 门禁 + 维护者 diff 复核共同保证；`CODEOWNERS` 在单一身份下退化为文档（见其文件头说明）。
- **接口变更流程**：任何对 §0.2 三契约的更改，代理**不得自行实施**——应写入仓库根的 `NOTES_FOR_MAINTAINER.md`，由维护者确认后修改 `book/`、`SCHEMA.md` 或附录 B，并更新相应 `schema_version`。
- **每次提交/PR 必须通过 §5.2 的 CI 门禁。** 当前 `check_data.py`/`check_api.py` 会因数据未对齐（B1）与指标未实现（WP-A）而**先红后绿**——这红色正是待办清单。

---

## 1. 工作包 WP-A：`camo-eval` 评测工具包

### 1.1 目标与价值
把第15章"统一标尺"落地为一个**可安装、经测试、数值可信**的 Python 包，覆盖识别/生成/鲁棒三类指标，成为本项目（及社区）评测的事实标准入口。当前状态：MAE 已实现 + 单元测试通过；S/E/加权F/FID/ASR 为占位桩。

### 1.2 接口契约（与专著的唯一耦合，**不可擅改**）
公开 API 必须与第15章正文及**附录 B** 完全一致：

```python
# camo_eval/metrics/detection.py
mae(pred, gt) -> float
weighted_f_measure(pred, gt, beta2: float = 1.0) -> float        # Margolin 2014
s_measure(pred, gt, alpha: float = 0.5) -> float                 # Fan 2017 (ICCV)
e_measure(pred, gt) -> dict   # {"adaptive":…, "mean":…, "max":…} # Fan 2018 (IJCAI)
f_measure(pred, gt) -> dict   # {"max":…, "mean":…, "adaptive":…}

# camo_eval/metrics/generation.py
fid(real_dir, fake_dir) -> float
lpips(img_a, img_b) -> float
deception_rate(detector, images, targets) -> float   # detector 为可插拔可调用对象

# camo_eval/metrics/robustness.py
attack_success_rate(clean_outputs, attacked_outputs, criterion) -> float
ap_drop(clean_ap: float, attacked_ap: float) -> float
transferability(asr_by_model: dict) -> dict

# camo_eval/runner.py
evaluate(pred_dir, gt_dir, metrics: list[str]) -> "ResultsTable"

# camo_eval/export.py
to_latex(results: "ResultsTable") -> str
to_markdown(results: "ResultsTable") -> str
```

### 1.3 输入/返回契约（技术规范）
- **输入**：`pred`、`gt` 为同尺寸 `numpy.ndarray`（HxW）；`pred` 接受 `[0,1]` float 或 `uint8 [0,255]`（内部统一归一化到 `[0,1]`）；`gt` 为二值（>0 视为前景）。尺寸不一致时按文档约定 resize（默认将 `pred` 双线性插值到 `gt` 尺寸）。
- **边界情形**：空 `gt`（全 0）、全 1、单像素、含 NaN —— 每个指标须有明确且经测试的行为（不得崩溃或返回 NaN 而不报错）。
- **确定性**：相同输入恒返回相同值；涉及随机性的（如 FID 的特征采样）须支持固定 `seed`。
- **依赖**：尽量轻量；FID/LPIPS 可封装成熟库（如 `pytorch-fid`/`torch-fidelity`、`lpips`），并作为**可选依赖**（`pip install camo-eval[generation]`），不让核心检测指标依赖 torch。

### 1.4 任务分解
- **A1 检测指标**（最高优先）：实现 `weighted_f_measure`、`s_measure`、`e_measure`、`f_measure`，硬化 `mae`。
- **A2 批量与运行器**：`evaluate(pred_dir, gt_dir, metrics)` 遍历数据集、对齐文件名、聚合为 `ResultsTable`。
- **A3 出表**：`to_latex` / `to_markdown`（第11章 SOTA 表、第15章示例直接调用）。
- **A4 生成指标**：封装 FID/LPIPS；定义 `deception_rate` 的检测器插件接口（先给参考实现 + 桩）。
- **A5 鲁棒指标**：实现 ASR、AP-drop、迁移性聚合（输入为检测器输出，定义清楚数据契约）。
- **A6 文档与示例**：README、docstring、与第15章一致的指标定义；提供一段可运行 quickstart。

### 1.5 验收/审计要求（WP-A）
1. **数值正确性（最关键）**：`s_measure`/`e_measure`/`weighted_f_measure`/`mae` 必须在公共小型 fixture 上与**参考实现**对齐，绝对误差 ≤ `1e-4`。推荐以广泛使用的 `PySODMetrics`（`lartpang/PySODMetrics`）为参照基准，并在 `tests/` 中固化对照用例与参照数值来源。
2. **测试**：`pytest` 全绿；语句覆盖率 ≥ 85%；每个指标含正常用例 + ≥3 个边界用例。
3. **接口一致**：公开 API 名称/签名与第15章附录 B **逐一核对一致**（CI 用 `inspect` 自动校验函数签名清单）。
4. **确定性与可复现**：固定 seed 下两次运行结果一致；`requirements`/`pyproject` 锁定版本范围。
5. **可安装**：`pip install -e camo-eval` 干净环境通过；`camo-eval --help`（若提供 CLI）可用。
6. **风格**：`ruff`/`black` 通过；公开函数有 docstring（含公式或文献出处）。

---

## 2. 工作包 WP-B：Awesome 列表 + `data/` 流水线

### 2.1 目标与价值
把分散的资源汇成**机器可读、可自动校验、显式致谢**的 Awesome 列表，且**唯一事实来源是 `data/*.yaml`**——`awesome/README.md` 由脚本生成，杜绝手工漂移。它同时为后续网站（WP-C）供数。

### 2.2 接口契约：`data/` 模式（冻结字段名）

```yaml
# data/papers.yaml （列表项）
- id: fan2020sinet                 # 唯一；与 references.bib 的 bibtex_key 同名
  title: "Camouflaged Object Detection"
  authors: ["Fan D-P", "Ji G-P", "…"]
  year: 2020
  venue: "CVPR"
  pillar: detection                # generation | detection | evaluation
  domain: intelligent              # physical | digital | intelligent
  perspective: ai                  # nature | war | art | ai
  task_tags: ["image-cod"]
  url: "https://…"                 # 必填且可访问
  code: "https://…"                # 可空
  bibtex_key: fan2020sinet         # 与 book/references.bib 对齐（告警级校验）
  notes: ""

# data/datasets.yaml
- id: cod10k
  name: "COD10K"
  task: image-cod
  modality: image                  # image | video | multispectral | multimodal
  size: "5,066 camo"
  splits: "3,040 train / 2,026 test"
  year: 2020
  url: "https://…"
  license: "…"
  bibtex_key: fan2020sinet
  notes: "78 subclasses"

# data/leaderboard.yaml
- dataset: COD10K
  method: SINet
  metrics: { Sm: null, Fw: null, Em: null, MAE: null }   # 未核实一律 null，禁止杜撰
  source: paper                    # paper | reproduced
  verified: false                  # 核实后置 true 并填来源
  protocol: "COD10K+CAMO train"
  url: "https://…"
```

### 2.3 任务分解
- **B1 锁定模式**：与作者确认上述字段（接口变更走 §0.3）；写 `data/SCHEMA.md`。
- **B2 充实条目**：从专著 `references.bib` 与权威综述沉淀，里程碑 ≥150 → ≥300 条；每条 URL 必须可访问、信息逐条核实。
- **B3 生成器**：`scripts/build_awesome.py` 读 `data/` → 渲染 `awesome/README.md`，按"三支柱 × 三域"+ 视角分类；输出**确定性**（同输入同输出，便于 diff）。
- **B4 链接检查**：接入/完善 `check-links` 工作流，全部 URL 必须解析通过。
- **B5 一致性 CI**：`scripts/check_data.py` 校验：① `awesome/README.md` 与生成器输出**逐字节一致**；② 无重复 `id`；③ `leaderboard` 中 `verified:false` 的项的 `metrics` 必须为 null 或显式标注；④ `bibtex_key` 与 `references.bib` 的对齐（**告警级**）。
- **B6 致谢与互链**：在列表顶部显式致谢并链接 visionxiang / ChunmingHe / clelouch / GuoleiSun 等现有列表（项目计划要求）。

### 2.4 验收/审计要求（WP-B）
1. **零杜撰**：`leaderboard.yaml` 中任何非空数值都必须 `verified:true` 且带 `source`/`url`；审计随机抽查 10 条回溯到原文。
2. **链接有效**：link-check CI 全绿（失效链接清零或标注 `dead:true` 并移出展示）。
3. **同源一致**：`awesome/README.md` 必须是 `build_awesome.py` 的产物（CI 重新生成后 `git diff` 为空）。
4. **去重与规范**：无重复 `id`；字段值符合枚举（pillar/domain/perspective/modality）。
5. **致谢到位**：现有 Awesome 列表均被致谢并互链。
6. **里程碑**：达到约定条目数（v1.0 ≥300）。

---

## 3.（后续）WP-C：网站骨架（按"稳定性优先"置后）

网站迭代最频繁，按项目路线图 Phase 3 启动。其与专著的接口同样是 `data/*.yaml`（VitePress 直接消费），故只要 §2.2 模式稳定，网站可在 WP-B 完成后独立推进：数据集页、论文/模型库页、排行榜（消费 `leaderboard.yaml`，只展示 `verified:true`）、Demo 入口。**本阶段暂不展开任务**，待 WP-A/B 验收后另发工作说明。

---

## 4. 里程碑与时间线（建议）

| 周次 | WP-A（camo-eval） | WP-B（awesome + data） |
|------|-------------------|------------------------|
| 第1周 | A1 检测指标 + 数值对标测试 | B1 锁模式 + B3 生成器骨架 |
| 第2周 | A2 运行器 + A3 出表 | B2 充实至 ≥150 条 + B4 链接检查 |
| 第3周 | A4 生成指标（FID/LPIPS） | B2 至 ≥300 + B5 一致性 CI |
| 第4周 | A5 鲁棒指标 + A6 文档 | B6 致谢互链 + 验收 |
| 验收 | `camo-eval v0.5` | `awesome v1.0` |

> 顺序仍遵循项目"稳定性优先"：WP-A（评价基础设施，相对稳定、且为第15章实证支撑）优先级最高；WP-B 紧随；WP-C 殿后。

---

## 5. 审计与验收总则（统一）

### 5.1 完成定义（Definition of Done，每个 PR）
- [ ] 满足对应工作包 §1.5 / §2.4 的全部条目
- [ ] 自动化门禁（§5.2）全绿
- [ ] 不触碰 `book/`（除非经 §0.3 接口变更流程）
- [ ] 含必要测试与文档；变更点在 PR 描述中对应到任务编号

### 5.2 自动化 CI 门禁（合并前必过）
1. **测试**：`pytest` 全绿；覆盖率不低于阈值（WP-A ≥85%）。
2. **数值对标**：camo-eval 指标对 `PySODMetrics` 参照值误差 ≤ `1e-4`（固化在 `tests/test_reference_values.py`）。
3. **接口签名校验**：自动比对公开 API 与第15章附录 B 的名单，不一致即失败。
4. **数据一致性**：`scripts/check_data.py` 通过（同源、去重、枚举合法、无杜撰）。
5. **链接检查**：`check-links` 全绿。
6. **构建**：`awesome/README.md` 可由生成器重建且 `git diff` 为空；`camo-eval` 可 `pip install -e`。
7. **风格**：`ruff` + `black --check` 通过。

### 5.3 人工评审清单（每个 PR）
- [ ] 数值正确性：对标来源是否权威、容差是否合理、边界用例是否覆盖
- [ ] 接口纪律：是否擅自改动 §0.2 三契约
- [ ] 无杜撰：leaderboard/数据条目是否每个数字可溯源
- [ ] 可复现：随机性是否受 seed 控制、依赖是否锁版本
- [ ] 文档：API 文档与第15章定义是否一致

### 5.4 专项审计（里程碑验收时）
- **数值审计**：抽取 ≥3 个数据集、≥3 个方法，用 camo-eval 复现并与原文/参照实现对照，记录差异与原因。
- **溯源审计**：随机抽查 `data/` 与 `leaderboard` 各 10 条，逐条回溯到原始出处。
- **可复现审计**：在干净环境从零 `pip install` + 跑通 quickstart 与一次完整 `evaluate`。
- **接口审计**：核对三契约与专著（附录 A/B、references.bib 键）一致。
- 通过后由维护者复核 CI 门禁与本节专项审计结果，**签发**对应版本（`camo-eval v0.5` / `awesome v1.0`）。

---

## 6. 帮手的"第一周"起步任务（可立刻开工）

1. 读 `docs/PROJECT_PLAN.md`、本文件、以及第15章 `.qmd` 与其附录 B（**只读**），理解接口契约。
2. 建分支 `wp-a/detection-metrics`：
   - 实现 `s_measure` / `e_measure` / `weighted_f_measure`，硬化 `mae`；
   - 写 `tests/test_reference_values.py`，`pip install pysodmetrics`，在 5–10 个小型 fixture 上对标，容差 `1e-4`；
   - 提 PR，确保 §5.2 门禁全绿。
3. 并行建分支 `wp-b/data-schema`：
   - 按 §2.2 写 `data/SCHEMA.md` 并校正现有三个 yaml 的字段；
   - 写 `scripts/build_awesome.py`（先跑通"读 yaml → 生成 README"的最小闭环）与 `scripts/check_data.py`；
   - 提 PR。

> 任何对接口契约（§0.2）的疑问，先开 `interface-change` Issue，不要直接改 `book/` 或擅改字段名。
