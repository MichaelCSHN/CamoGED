# CODEX 开工指令 · Sprint 1

> 致 Codex：你负责本仓库的**代码 / 数据 / Awesome / 网站**；专著（`book/`）由维护者与 Claude 负责，你不参与其写作。
> **开工前必读**（仓库内，按顺序）：`AGENTS.md` → `docs/CONTRIBUTOR_WORK_PACKAGES.md` → `data/SCHEMA.md`。
> 本指令只覆盖 **Sprint 1**；完成并通过审计后再下发下一轮。

---

## 0. 纪律（每次提交都适用）

1. **边界**：只改 `camo-eval/ data/ awesome/ scripts/ web/` 及其测试与相关 `.github/workflows/`。
   **绝不修改 `book/`（含 `references.bib`、`figures/`、任何 `*.qmd`）。** 这是硬规则。
   > 说明：此前对 `ch1/ch15/references.bib` 的直接修改属越界，本轮一次性接受，**从现在起不再允许**。
2. **需要动到 `book/` 或三个冻结接口时**：不要自己改，写进仓库根 `NOTES_FOR_MAINTAINER.md`（用其条目格式），然后继续做允许做的部分。新引用键也走这条通道——你可在 `data/*.yaml` 使用键名，但**不得编辑 `references.bib`**。
3. **零杜撰**：指标值、排行榜数字、数据规模/划分、引用、URL、DOI 一律不得编造；未知即 `null`。`leaderboard` 中任何非 null 数值必须 `verified: true` 且 `source` 可解析。
4. **完成即自检**（见 §3）：未全绿不得声称完成。

---

## 1. 任务 A（WP-A/A1）：实现检测指标并对标

**分支**：`wp-a/detection-metrics`

1. 按 `AGENTS.md` §6 的**冻结签名**实现 / 硬化：
   `mae`、`weighted_f_measure(pred, gt, beta2=1.0)`、`s_measure(pred, gt, alpha=0.5)`、
   `e_measure(pred, gt) -> dict`、`f_measure(pred, gt) -> dict`。函数名/参数名**不得改动**。
2. 遵守输入契约：`pred`/`gt` 同尺寸 `ndarray`；`pred` 接受 `[0,1]` float 或 `uint8[0,255]`（内部归一化）；`gt` 二值。为空/全前景/单像素/NaN 等边界写明确行为并测试。核心检测指标**不得依赖 torch**。
3. **数值对标**：`pip install pysodmetrics`，在 `tests/test_reference_values.py` 用 5–10 个小 fixture 与之对比，绝对误差 ≤ `1e-4`，并在测试中注明参照来源。
4. 目标：`python scripts/check_api.py` 的**检测部分全绿**（generation 因可选重依赖仍可为 WARN）；`pytest` 全绿、camo-eval 覆盖率 ≥ 85%。

**本轮不做**：生成/鲁棒指标只保留脚手架与签名即可（FID/LPIPS 等放可选 extra，不实现细节）；**不得新增** `metrics/human`、`metrics/signature` 等契约外指标族（需先走接口变更）。

---

## 2. 任务 B（WP-B/B1）：把 `data/*.yaml` 对齐到 SCHEMA

**分支**：`wp-b/data-align`

1. 按 `data/SCHEMA.md` 补齐必填字段：`papers` 加 `id`、`perspective`、`bibtex_key`；`datasets` 加 `id`、`year`、`license`、`bibtex_key`；`leaderboard` 加 `verified`（默认 `false`），并把 `dataset` 改为引用 `datasets.id`。
2. 按 `SCHEMA.md §8` 的**映射表**修正越界词表值（如 `military-cod→image-cod`、`multispectral-cod→image-cod`、`adversarial→physical-adversarial`、`cross-domain→application`、`rgb-video→video` 等）。
3. `bibtex_key` 尽量复用维护者已合并的 `references.bib`（现 69 条）中的键；**缺键写入 `NOTES_FOR_MAINTAINER.md`**，不要碰 `references.bib`。
4. **不要填任何未核实的数字**：`leaderboard` 的 metrics 维持 `null`、`verified:false`，直到逐条核实（核实属后续任务，本轮只做结构对齐）。
5. 目标：`python scripts/check_data.py` **全绿**（0 error；bibtex_key 的 WARN 可保留并在 NOTES 列出）。

---

## 3. 完成定义（DoD · 每个任务提交前必须全绿）

```bash
pytest -q                              # 全绿；camo-eval 覆盖率 >= 85%
python scripts/check_data.py           # 0 error
python scripts/check_api.py            # 检测部分 0 error（generation 可 WARN）
ruff check . && black --check .        # 风格
git diff --name-only | grep '^book/'   # 必须为空（未触碰 book/）
```

提交规范：一个任务一条（或一组）提交，信息注明工作包号，如
`feat(camo-eval): WP-A/A1 implement s/e/weighted-F + PySODMetrics tests`、
`data: WP-B/B1 align yaml to SCHEMA v1.0`。

---

## 4. 交付与送审流程

1. 完成任一任务后，跑通 §3 全部门禁。
2. 在提交信息或 `CHANGELOG`（可新建 `CHANGELOG.md`，属你可写区）中**列出本次改了什么、对标结果、覆盖率**。
3. 任何阻塞、缺键、或需动 `book/`/接口的事项，写入 `NOTES_FOR_MAINTAINER.md`。
4. 通知维护者；维护者把改动文件/diff 交给 Claude **审计**。

## 5. Claude 的审计标准（你据此自检即可一次通过）

- **数值正确性**：抽 ≥3 个 fixture，camo-eval 输出对 PySODMetrics 误差 ≤ `1e-4`。
- **接口一致**：`check_api.py` 检测部分全绿，公开签名与 `AGENTS.md §6` 逐一吻合。
- **schema 合规 + 零杜撰**：`check_data.py` 0 error；随机抽查 leaderboard/data 条目可溯源，无编造数字。
- **边界**：本次提交未触碰 `book/`。
- **可复现**：干净环境 `pip install -e camo-eval` + 跑通；随机性受 seed 控制。
- 全部通过 → 该任务**验收**；否则退回并附问题清单。

---

## 6. 本轮不在范围内（勿做）

- 网站 `web/`（WP-C，后续）。
- 生成/鲁棒指标的完整实现（仅签名脚手架）。
- 任何对三个冻结接口（`data/SCHEMA.md` 字段/词表、`camo-eval` 公开 API、`bibtex_key` 命名空间）的更改——必须先经 `NOTES_FOR_MAINTAINER.md` 由维护者批准。
- 编辑 `book/` 任何文件。

> 起步顺序建议：先 §1 任务 A 与 §2 任务 B 并行（两条分支），各自把对应的 CI 门禁从红刷绿。完成即送审。
