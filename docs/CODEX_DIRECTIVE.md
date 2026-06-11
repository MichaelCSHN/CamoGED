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

## 1. 任务 A：专著（`book/`）—— 你现在是作者

1. **章节扩写到出版级**：按既有风格（导读 callout、分节、`@tbl-`/`@fig-` 交叉引用、`[@key]` 引用）逐章充实。
2. **引用**：你现在**同时拥有 `book/references.bib` 与 `data/*.yaml` 的 `bibtex_key`**。新增引用时，
   在 `references.bib` 加条目并让 `data/*.yaml` 的 `bibtex_key` 与之同名同义——**在同一次提交里对齐**。
   - 立即处理 `NOTES_FOR_MAINTAINER.md` 中的 `cam3d2025`：现在由你直接在 `references.bib` 补键并对齐 `data/papers.yaml`，完成后删除该 NOTES 条目。
3. **配图**：用 Quarto 代码块/外部图生成 `book/.../figures/`；确保 `quarto render` 能重建，不提交可由代码生成的中间产物以外的大二进制。
4. **审校**：术语一致、跨章引用不断链、无事实/日期/引用杜撰（**零杜撰铁律同样适用于书稿**）。
5. **与 camo-eval 的一致性**：第15章与附录 B 的指标定义须与 `AGENTS.md §6` 的公开 API 保持一致。
   若你认为 API 需要改动，**不要自己改 camo-eval**——写入 `NOTES_FOR_MAINTAINER.md` 交 Claude。

**book DoD**：`quarto render` 无错误；引用全部解析；图全部生成；无断裂交叉引用。

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
