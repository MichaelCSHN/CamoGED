# CODEX 指令 · Sprint 2（专著 + Awesome）

> 致 Codex：分工已调整（见 `AGENTS.md` 抬头与 `docs/CONTRIBUTOR_WORK_PACKAGES.md` §0.1）。
> 本指令取代 `docs/CODEX_KICKOFF.md`（Sprint 1）的分工部分。**开工前按顺序读**：
> `AGENTS.md` → 本文件 → `data/SCHEMA.md`。

---

## 0. 新分工（一句话）

- **Claude（主管）** 接手 `camo-eval/` 的全部开发与实跑，含 `web/hf-space/`、`camo-eval/notebooks/`、`scripts/check_api.py`。
- **你（Codex）** 专注两件事：**① 专著写作**（`book/`：章节扩写、配图、引用、审校）；**② Awesome 模块**（`awesome/` + `data/` + `scripts/build_awesome.py` + `scripts/check_data.py` + 数据驱动的 `web/` 页面）。

**从现在起不要再改 `camo-eval/`、`scripts/check_api.py`、`web/hf-space/`、`camo-eval/notebooks/`。**
你此前在 `wp-a/detection-metrics` 上对 camo-eval 的工作已被接收，后续由 Claude 维护与整改。

---

## 1. 任务 A：专著（`book/`）—— 扩充各章至规定字数

**目标**：把各章正文扩充到 `docs/BOOK_COMPILATION_PLAN.md` 规定的字数。当前全书约 7.0 万字，
目标约 20.8 万字（详见下表，缺口很大）。**以中文正文字数计**（不含代码/表格/英文）。

| 章节 | 现字数 | 目标字数 | 达成 |
|---|---:|---:|---:|
| 01 伪装的本质与统一框架 | 8,189 | 12,000 | 68% |
| 02 自然界的伪装 | 5,470 | 16,000 | 34% |
| 03 军事伪装 | 4,775 | 18,000 | 26% |
| 04 伪装在艺术与文化中 | 3,595 | 12,000 | 29% |
| 05 物理域伪装生成 | 4,264 | 12,000 | 35% |
| 06 物理对抗伪装 | 4,754 | 16,000 | 29% |
| 07 数字域伪装生成 | 4,409 | 11,000 | 40% |
| 08 智能域伪装生成 | 4,283 | 13,000 | 32% |
| 09 物理与数字域识别 | 3,961 | 12,000 | 33% |
| 10 智能域识别总览与数据集 | 3,423 | 10,000 | 34% |
| 11 图像伪装目标检测 | 3,635 | 16,000 | 22% |
| 12 视频伪装目标检测 | 3,396 | 12,000 | 28% |
| 13 实例级与扩展任务 | 3,441 | 11,000 | 31% |
| 14 基础模型时代的识别 | 3,471 | 11,000 | 31% |
| 15 伪装评价的统一标尺 | 4,709 | 16,000 | 29% |
| 16 前沿、挑战与展望 | 3,789 | 10,000 | 37% |

> 自查字数：`python3 -c "import re,sys;print(len(re.findall(r'[一-鿿]',open(sys.argv[1]).read())))" book/chapters/XX.qmd`

**硬约束（必须遵守，违反即退回）**：
1. **不得随意改动一级 / 二级标题**（`#`、`##`，含 `{#sec-...}` 锚点与现有编号）。标题体系已与全书导航、交叉引用绑定。
   确需调整标题须先写入 `NOTES_FOR_MAINTAINER.md` 等确认。三级及以下（`###`+）可按需新增以承载新内容。
2. **行文语气、风格遵照原书稿**：沿用既有的导读 `::: {.callout-tip}` 体例、分节叙述节奏、术语与人称；扩写是"加深加厚"，不是改写已定稿的论述。
3. **页面布局与图表风格遵照原书稿**：图表用既有的 `@fig-`/`@tbl-` 交叉引用与 caption 样式、统一配色/字体（见 `docs/BOOK_COMPILATION_PLAN.md` 视觉规范）；新增图表沿用同一风格，不引入新的排版样式。
4. **零杜撰**：新增的事实、数字、年代、引用必须可溯源；新引用同步进 `references.bib` 并对齐 `data/*.yaml` 的 `bibtex_key`（你现在两侧都拥有）。
5. **立即处理** `NOTES_FOR_MAINTAINER.md` 中的 `cam3d2025`：在 `references.bib` 补键并对齐 `data/papers.yaml`，完成后删除该 NOTES 条目。

**扩写方法建议**：按 `docs/BOOK_COMPILATION_PLAN.md` 各章"核心内容/关键文献/必备图表"清单逐条落实——
补全缺失小节、加深论证与案例、补关键文献与史料、补必备图表，而非空洞灌水。

**与 camo-eval 的一致性**：第15章与附录 B 的指标定义须与 `AGENTS.md §6` 的公开 API 一致；
若认为 API 需变动，**不要改 camo-eval**——写入 `NOTES_FOR_MAINTAINER.md` 交 Claude。

**book DoD**：`quarto render` 无错误；引用全部解析；图全部生成；无断裂交叉引用；各章字数达标（或在 NOTES 说明合理偏差）。

## 2. 任务 B：Awesome 模块（`awesome/` + `data/`）

接续 WP-B：
1. **充实条目**：`data/papers.yaml` / `datasets.yaml` 从现状扩到里程碑（v1.0 ≥300 条），每条 URL 可访问、逐条核实。
2. **生成器确定性**：`scripts/build_awesome.py` 读 `data/` → 渲染 `awesome/README.md`，同输入同输出。
3. **一致性 / 链接 / 致谢**：`scripts/check_data.py` 全绿；link-check 工作流全绿；顶部致谢并互链现有 Awesome 列表。
4. **零杜撰**：`leaderboard.yaml` 任何非 null 数值须 `verified:true` 且 `source` 可解析。

**awesome DoD**：
```bash
python scripts/check_data.py            # 0 error
python scripts/build_awesome.py && git diff --exit-code awesome/README.md   # 同源一致
# link-check 工作流全绿
```

## 3. 边界自检（每次提交前）

```bash
# 必须为空：你不应触碰 Claude 拥有的区域
git diff --name-only | grep -E '^(camo-eval/|scripts/check_api\.py|web/hf-space/)'
```

## 4. 分支与提交

- **不要再把 book/ 与 camo-eval/ 混在同一提交/分支**（此前 `wp-a/detection-metrics` 同时含两者，今后分开）。
- 建议分支：书稿 `book/<chapter>`；Awesome `wp-b/<task>`。
- 提交信息标注范围：`docs(book): …`、`data: …`、`feat(awesome): …`。

## 5. 需要 Claude 配合时

任何 camo-eval 缺陷、想在排行榜/网站暴露的新指标、或需要改动冻结接口的事项 → 写入 `NOTES_FOR_MAINTAINER.md`，不要自行实现。
