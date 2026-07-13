#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def patch(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'marker not found in {path}: {old[:80]}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Appendix: explain curated/catalog split and multi-axis schema.
patch('book/chapters/appendix-resources.qmd',
'''书中数据集表由 `data/datasets.yaml` 生成。正式版本只展示已核验记录，每条至少包含：名称、任务、模态、规模、正式划分、标注粒度、论文或官方页面、许可证、发布状态、最后核验日期与备注。项目只提供导航和校验信息，不重新分发受限数据。''',
'''仓库现维护两个不同层级的资源表面：**Awesome Camouflage** 是人工精选的阅读地图；**CamoGED Research Catalog** 是完整的、Schema 驱动的已接受元数据目录。自动发现只能产生候选，不会直接进入任一正式表面；Catalog 条目默认仅为 `metadata-only`，进入精选 Awesome 还需要独立的人工编辑决定。

书中数据集表由 `data/datasets.yaml` 生成。正式版本只展示已核验记录，每条至少包含：名称、任务、模态、规模、正式划分、标注粒度、论文或官方页面、许可证、发布状态、最后核验日期与备注。项目只提供导航和校验信息，不重新分发受限数据。资源分类采用多轴字段：资源类型、支柱、任务、模态、监督方式、方法族、应用语境和策展等级；旧的单值 `pillar/domain/task` 仅为兼容字段。''')
patch('book/chapters/appendix-resources.qmd',
'''- 动态资源：网站 `/papers`、`/datasets`、`/leaderboard`、`/demo`''',
'''- 人工精选阅读地图：网站 `/awesome`
- 完整研究目录与筛选器：网站 `/catalog`
- 自动扫描状态：网站 `/updates`（只读读取 GitHub 候选 Issue）
- 其他动态资源：网站 `/datasets`、`/leaderboard`、`/demo`''')

# Chapter 10: expand task map without pretending all categories are equally mature.
marker = ': COD 任务谱系（按复杂度递增） {#tbl-tasks}'
addition = marker + '''

::: {.callout-note}
## 动态任务地图：2026 年版补充

随着数据与基础模型的发展，任务谱系还应沿另外四条轴展开：**输出粒度**（二值掩膜、实例掩膜、边界框与轨迹）、**监督强度**（全监督、弱监督、半监督、无监督与零样本）、**语义开放度**（封闭类别、指代、开放词汇与视觉语言推理）以及**观测模态**（RGB、深度、热红外、偏振、多/高光谱与多模态）。因此，bbox 型现实 COD、伪装目标跟踪、不完整监督、零样本/开放词汇、VLM 评价和腐蚀鲁棒性不应再被视为图像 COD 的附注，而应在协议中单独登记。

这些类别来自动态 Catalog 的任务分面；它们说明研究版图已扩展，并不意味着各分支已经形成同样稳定的数据集、指标或公认基准。书稿只在完成一手来源核验后引用具体工作，Catalog 的 `metadata-only` 条目不自动构成正文证据。
:::
'''
patch('book/chapters/10-intelligent-overview-datasets.qmd', marker, addition)

# Chapter 14: add a bounded recent-work window.
p = ROOT / 'book/chapters/14-foundation-models.qmd'
text = p.read_text(encoding='utf-8')
recent = '''

## 14.9 动态文献窗口：2025—2026 年基础模型方向 {#sec-foundation-dynamic-window}

截至 2026 年 7 月，动态 Catalog 已出现若干值得后续书目核验的方向：面向伪装视频的 SAM2 适配与自动提示（如 CamSAM2、CamoSAM2），面向大视觉语言模型的细粒度伪装场景评价（如 MMCSBench），以及开放词汇、零样本和 bbox 型伪装识别的新任务设置。它们共同表明，研究重点正在从“替换骨干”转向**提示初始化、记忆纠错、语义开放性、跨任务协议和基础模型能力诊断**。

本节是版本化的检索窗口，不是正式综述结论。上述条目在 Catalog 中仍可能处于 `metadata-only` 或预印本状态；出版版只有在核对正式出版身份、代码/数据可用性、任务定义和实验协议后，才应将其写入正文参考文献或据此作“最新”“首个”“最优”等判断。
'''
if '## 14.9 动态文献窗口' not in text:
    p.write_text(text.rstrip() + recent + '\n', encoding='utf-8')

# Fact-check register: recurring dynamic claims gate.
p = ROOT / 'docs/BOOK_FACTCHECK_REGISTER.md'
text = p.read_text(encoding='utf-8')
row = '| F15 | 全书 | “首个/最大/最新/SOTA”动态主张 | OPEN | 每次出版候选冻结前，依据 Catalog 最近人工审核日、正式出版源和任务定义重新核验；自动候选不得直接支持正文主张。 |\n'
if 'F15' not in text:
    p.write_text(text.rstrip() + '\n' + row, encoding='utf-8')

# Demo remains synthetic; add navigation and evidence boundary.
p = ROOT / 'web/demo.md'
text = p.read_text(encoding='utf-8')
extra = '''

## Scope and provenance

This remains a deterministic synthetic teaching tool. It does not run any catalogued model and does not treat inclusion in Awesome as reproduction evidence.

- Browse task and model metadata in the [Research Catalog](./catalog.md).
- Check which evaluation functions are validated or experimental in the [camo-eval validation register](https://github.com/MichaelCSHN/CamoGED/blob/main/camo-eval/VALIDATION.md).
- A future model-backed demo requires fixed code and weight provenance, an explicit license, an evaluation manifest, and an independently reviewable report.
'''
if '## Scope and provenance' not in text:
    p.write_text(text.rstrip() + extra + '\n', encoding='utf-8')

# Register interactive components.
patch('web/.vitepress/theme/index.js',
'''import CamoDemo from "./components/CamoDemo.vue";''',
'''import CamoDemo from "./components/CamoDemo.vue";
import CatalogExplorer from "./components/CatalogExplorer.vue";
import ScanStatus from "./components/ScanStatus.vue";''')
patch('web/.vitepress/theme/index.js',
'''    app.component("CamoDemo", CamoDemo);''',
'''    app.component("CamoDemo", CamoDemo);
    app.component("CatalogExplorer", CatalogExplorer);
    app.component("ScanStatus", ScanStatus);''')

# Generator emits interactive components and catalog JSON.
p = ROOT / 'scripts/build_awesome.py'
text = p.read_text(encoding='utf-8')
text = text.replace('"## All resources",\n        "",\n        "| Year | Resource | Type | Tasks | Modalities | Supervision | Status | Links |",',
'''"## Interactive explorer",\n        "",\n        "<CatalogExplorer />",\n        "",\n        "## All resources",\n        "",\n        "| Year | Resource | Type | Tasks | Modalities | Supervision | Status | Links |",''')
text = text.replace('"- Automated scan: see the latest GitHub issue labeled `awesome:triage`.",',
'''"<ScanStatus />",\n        "",\n        "- Automated scan history is read from public GitHub issues labeled `awesome:triage`.",''')
text = text.replace('write(WEB / "catalog.md", render_catalog(resources, config))',
'''write(WEB / "catalog.md", render_catalog(resources, config))
    import json
    (WEB / "public" / "catalog-data.json").parent.mkdir(parents=True, exist_ok=True)
    (WEB / "public" / "catalog-data.json").write_text(json.dumps(resources, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")''')
p.write_text(text, encoding='utf-8')

print('cross-component backlog applied')
