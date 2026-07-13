#!/usr/bin/env python3
"""Apply the applicable findings from BOOK_REVIEW_20260713 to the active book branch."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str, *, count: int = 1) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} occurrence(s), found {actual}: {old[:80]!r}")
    target.write_text(text.replace(old, new, count), encoding="utf-8")


# 1. Chapter-summary style and updated evaluation-part references.
replace(
    "book/chapters/06-physical-adversarial.qmd",
    '''带着这套问题进入后续章节，读者会更容易判断一种伪装技术究竟是在改变物理外观、改变机器表征，还是改变评价协议本身。\n\n这也是本书反复强调"隐藏"与"揭示"必须成对理解的原因。\n\n只有把两者放在同一评价场中，物理对抗伪装才不会被误读为孤立的模型故障。\n\n这也是本章的最终落点。\n\n''',
    "",
)
replace(
    "book/chapters/06-physical-adversarial.qmd",
    '也推动了评价篇对"多维 scorecard"的需求（第 15 章）',
    '也推动了评价篇对"多维 scorecard"的需求（第 15—20 章）',
)
replace(
    "book/chapters/06-physical-adversarial.qmd",
    "与第 15 章评价相比",
    "与第 15—20 章评价篇相比",
)
replace(
    "book/chapters/06-physical-adversarial.qmd",
    "第 15 章再把这些生成和识别问题放回统一评价框架",
    "第 15—20 章再把这些生成和识别问题放回统一评价框架",
)
replace(
    "book/chapters/06-physical-adversarial.qmd",
    "第 15 章 `camo-eval` 鲁棒性指标",
    "第 15、20 章评价协议与 `camo-eval` 验证边界",
)

replace(
    "book/chapters/09-physical-digital-detection.qmd",
    '''证据空间越宽，单一伪装策略越难长期成立。\n\n这就是揭示方的长期优势。\n\n也是第三篇展开的起点。\n\n从此开始，搜索者登场。\n\n并不断扩大视野。\n\n直到目标最终显形。\n\n''',
    "",
)
replace(
    "book/chapters/09-physical-digital-detection.qmd",
    "这正是第 15 章统一标尺的要求",
    "这正是第 15—20 章评价篇的要求",
)
replace(
    "book/chapters/09-physical-digital-detection.qmd",
    "面向第 15 章，本文给出的信道表也提示了评价工具的设计方向",
    "面向第四篇评价，本章给出的信道表也提示了评价记录的设计方向",
)

replace(
    "book/chapters/14-foundation-models.qmd",
    '''评价因此不是附录，而是连接生成、识别与应用决策的主轴。\n\n这也是全书第四篇的起点。\n\n评价框架由此展开。\n\n''',
    "",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "第 15 章必须处理的正是这种复杂性",
    "第四篇评价必须处理的正是这种复杂性",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "这三个限定语正是第 15 章评价框架要系统回答的问题",
    "这三个限定语正是第 15—20 章评价体系要系统回答的问题",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "SAM 破解边界扩展问题，CLIP 破解开放语义问题，DINO 破解无类别对象性问题，MLLM 破解机制解释问题，视频基础模型破解时序持久性问题；每一种说法都需要对应的消融、可视化和外部验证。",
    "SAM 可提供候选边界与交互分割能力，CLIP 可提供开放语义信号，DINO 类特征可提供无类别对象性，MLLM 可提供语言解释接口，视频基础模型可提供时序记忆；这些能力是否真正缓解对应伪装机制，仍需逐项消融、可视化和外部验证。",
)
replace(
    "book/chapters/14-foundation-models.qmd",
    "第15章将检验这些能力扩展是否在可比协议下带来真实收益。",
    "第15—20章将检验这些能力扩展是否在可比协议下带来真实收益。",
)

# 2. Research-agenda projects must not be presented as completed methods.
replace(
    "book/chapters/08-intelligent-generation.qmd",
    "计划中提到的 SCODE 类合成数据增强路线，可以放在同一谱系中理解：其核心不是某个模型名字，而是把合成数据作为 COD 训练分布的主动补充。",
    "更一般的合成数据增强路线可以放在同一谱系中理解：其核心不是追逐某个模型名字，而是把可核验的合成数据作为 COD 训练分布的主动补充。",
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    "flowcamo 则把问题推进到视频和运动。",
    "作者研究议程 `flowcamo` 拟把问题推进到视频和运动，但尚不作为既成方法。",
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    "| flowcamo | 视频帧、光流、掩膜 | 时序一致、运动感知难例 | 光流误差、闪烁、标注传播误差 | 视频 $\\mathcal{J}\\&\\mathcal{F}$、时序稳定性 |",
    "| `flowcamo`（研究议程） | 拟研究：视频帧、运动线索、掩膜 | 拟研究：时序一致与运动感知难例 | 尚无公开核验架构、消融或结果 | 预注册后评价视频空间质量、持续检出与真实集泛化 |",
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    '''这张表也说明，智能域生成不能只有一个 demo。更合理的组织方式，是按方法族和指标族做成可切换模块：用户选择一种生成方式，再选择相似度、感知质量、检测影响和鲁棒性指标，观察同一输入在不同方法下如何变化。这样既能展示生成图，也能展示 score、mask、边界、检测框和失败案例，符合本项目"能跑、能看、能比较"的务实路线。''',
    '''这张表也提示，教学示意不应只展示单张生成图。更合理的呈现方式，是按方法族与证据类型组织对照，同时展示相似度、感知质量、检测影响、鲁棒性和失败案例。具体交互界面与软件路线属于项目文档；正文只保留评价逻辑。''',
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    '''在 demo 层面，生成服务于检测可以做成可运行的最小闭环：给定一组真实背景、目标掩膜和目标图，用户选择 copy-paste、泊松融合、风格迁移或扩散增强，系统输出合成样本、掩膜、FID/LPIPS/目标-背景相似度和检测器置信度变化。这样的 demo 不需要训练重模型，也能让读者看到不同生成策略对评价指标的影响。若再加入一个轻量检测器或预计算检测结果，就能展示"生成难例如何改变检测表现"。''',
    '''教学实验可以用固定背景、目标掩膜和预计算输出，对照 copy-paste、泊松融合、风格迁移或扩散增强，并同时展示合成样本、掩膜、标准实现可用时的感知指标、目标—背景相似度和检测响应。该示意用于解释证据链，不代表当前在线 Demo 已接入这些生成器或标准指标。''',
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    "如 CamDiff 或 SCODE 类合成样本",
    "如 CamDiff 等经来源核验的智能生成样本",
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    "才按第10章协议和第15章指标回填正式方法内容",
    "才按第10章协议和第15—20章评价规则回填正式方法内容",
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    '#| fig-cap: "格拉姆统计与伪装质量代理示意。左列：三种纹理（背景/伪装目标/非伪装目标）。右列：对应的格拉姆矩阵（基于多尺度定向滤波器组特征的协方差）。伪装目标与背景的格拉姆统计接近（低风格距离），非伪装目标远离背景（高风格距离）——风格距离可作为\'藏得有多好\'的度量代理。"',
    '#| fig-cap: "格拉姆统计的固定种子教学示意。左列为三种合成纹理，右列为多尺度定向滤波器特征的协方差描述。本次示意中，同尺度纹理的代理距离小于异尺度纹理；该结果只说明代理量方向，不证明真实伪装有效性或人类可检测性。"',
)
replace(
    "book/chapters/08-intelligent-generation.qmd",
    "plt.suptitle('Gram-matrix style distance as a camouflage quality proxy', fontsize=10)",
    "plt.suptitle('Gram-matrix descriptor distance: fixed-seed teaching example', fontsize=10)",
)

replace(
    "book/chapters/12-video-cod.qmd",
    "| flowcamo | 运动-外观双路闭环 | 与生成分支统一 | 需严格协议验证 |",
    "| `flowcamo`（研究议程） | 拟研究：运动—外观联合约束 | 拟连接生成与检测问题 | 尚无公开核验架构或结果 |",
)
replace(
    "book/chapters/12-video-cod.qmd",
    "SAM2 把时间转化为对象持久性；flowcamo 则尝试把时间同时用于生成和检测闭环。",
    "SAM2 把时间转化为对象持久性；作者研究议程 `flowcamo` 拟探索时间线索能否同时服务生成与检测闭环，但当前不作为已完成方法。",
)

replace(
    "book/chapters/13-instance-extended.qmd",
    "用户输入文本，例如",
    "查询者输入文本，例如",
    count=1,
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "用户可能输入具体物种、上位类别或功能描述",
    "查询者可能输入具体物种、上位类别或功能描述",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "若用户输入图中不存在的类别",
    "若查询中给出图中不存在的类别",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "| dualvcod | 视频实例与 ID | 跨帧实例轨迹 | ID switch、遮挡 | 视频监控、行为分析 |",
    "| `dualvcod`（研究议程） | 拟研究：视频实例与身份保持 | 拟输出：跨帧实例轨迹 | 尚无公开核验架构或结果 | 视频实例研究议程 |",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "| dualvcod | ID switch | 外观相似、遮挡重现 | ID switch、轨迹图 |",
    "| `dualvcod`（研究议程） | 拟重点检查 ID switch | 外观相似、遮挡重现 | 预注册后报告 ID switch 与轨迹证据 |",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "实例任务增加对象粒度，视频实例增加时间身份，指代任务增加语言，协同任务增加图组，开放词汇增加外部知识。",
    "实例任务增加对象粒度；视频实例任务增加时间身份，而 `dualvcod` 仅作为这一方向的作者研究议程；指代任务增加语言，协同任务增加图组，开放词汇增加外部知识。",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    '''对项目实现而言，dualvcod demo 可作为扩展任务入口：展示二值 mask、实例 mask、视频 ID 和轨迹；R-COD demo 可展示语言提示如何改变目标；Co-COD demo 可展示多图共同目标；OV-COS demo 可展示不同文本类别提示。若资源有限，可以先用预计算示例和轻量模型展示任务逻辑，再逐步接入完整模型。''',
    '''教学材料可以用预计算示例分别说明二值 mask、实例 mask、视频身份、语言指代、图组共同性和开放类别提示。`dualvcod` 只有在公开架构、固定协议和独立复现齐备后，才可作为模型示例；当前正文不承诺在线接入。''',
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "本章也与第 15 章评价紧密相关",
    "本章也与第 15—20 章评价篇紧密相关",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "第 15 章的统一评价应提供任务化协议",
    "第 15—20 章的统一评价体系应提供任务化协议",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "从 CIS 到计数、排序、dualvcod",
    "从 CIS 到计数、排序以及视频实例研究议程",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    "本章的 R-COD、OV-COS、CIS 和 dualvcod 都需要这些能力",
    "本章的 R-COD、OV-COS、CIS 以及视频实例方向都需要这些能力",
)
replace(
    "book/chapters/13-instance-extended.qmd",
    '''对项目实现而言，扩展任务不必一次全部做成重模型 demo。可以采用分层路线：先用静态示例展示 CIS 与计数；再用预计算视频展示 dualvcod 的 ID 轨迹；再用轻量视觉语言模型或预计算结果展示 R-COD/OV-COS；最后把这些任务接入统一 `camo-eval` 报告。这样既能覆盖任务谱系，又避免过早依赖重模型在线推理。''',
    '''扩展任务的教学呈现可以分层：静态示例解释 CIS 与计数，预计算视频解释身份保持，预计算图文结果解释 R-COD/OV-COS，最后用统一报告结构对照任务差异。软件接入顺序属于项目路线，不在正文中预先承诺。''',
)

# 3. Publishing voice, references, and terminology.
replace(
    "book/chapters/02-natural-camouflage.qmd",
    "第 5 章（[@sec-pattern-design]）",
    "第 5 章（@sec-pattern-design）",
)
replace(
    "book/chapters/02-natural-camouflage.qmd",
    "第 10 章（[@sec-protocol]）",
    "第 10 章（@sec-protocol）",
)

replace(
    "book/chapters/11-image-cod.qmd",
    '''图像伪装目标检测（Image COD）是智能域识别的核心，也是当前方法最密集、数据集最完备的子领域。本章以**思想脉络**而非方法列举为导向：先厘清传统方法的局限（11.1），再沿"搜索-识别"（11.2）→ 结构建模（11.3）→ 频域线索（11.4）→ 图与序列（11.5）→ 弱/半监督（11.6）的演进逻辑展开，每一步都指向同一问题：**如何在目标与背景统计近乎一致的条件下，捕捉那一点点结构性差异**；最后详述原创方法 **coder** （11.7）。''',
    '''图像伪装目标检测（Image COD）是智能域识别的核心，也是方法与数据较为集中的子领域。本章以**思想脉络**而非方法列举为导向：先厘清传统方法的局限（11.1），再沿“搜索—识别”（11.2）→ 结构建模（11.3）→ 频域线索（11.4）→ 图与序列（11.5）→ 弱/半监督（11.6）的演进逻辑展开；11.7 以作者研究议程 `coder` 标明尚未发表的边界，11.8 总结方法演进主线。各节共同回答：**如何在目标与背景统计近乎一致的条件下，捕捉有限而分散的结构性差异。**''',
)
replace(
    "book/chapters/11-image-cod.qmd",
    "PFNet 所谓 prohibition 的思想",
    "PFNet 的干扰挖掘与背景抑制思想",
)
replace(
    "book/chapters/11-image-cod.qmd",
    "第 15 章 `camo-eval` 中的背景相似度、边界质量和频域统计指标",
    "第 15—20 章评价篇与 `camo-eval` 中的背景相似度、边界质量和频域描述量",
)
replace(
    "book/chapters/11-image-cod.qmd",
    '''从平台角度看，弱/半监督方法尤其适合 demo：用户可以选择少量 scribble、框或自动伪标签，观察模型如何扩展成完整掩膜。这种交互能帮助理解 COD 标注为什么难，也能展示 `camo-eval` 如何评价弱监督输出与真值之间的差异。''',
    '''教学示意可以用少量 scribble、边界框或预计算伪标签，说明弱监督如何扩展为完整掩膜，并展示输出与真值之间的差异。该示意用于解释标注问题，不代表当前 Demo 已接入在线训练或重模型推理。''',
)
replace(
    "book/chapters/11-image-cod.qmd",
    "第 15 章 `camo-eval`。",
    "第 15—20 章评价篇与 `camo-eval/VALIDATION.md`。",
)

# 4. Figure-caption truthfulness and dataset table closure.
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    '''下面的示例说明为何 S-measure 和 MAE 会给出不一致的排名——这是 COD 评价不能"只看 MAE"的典型案例：''',
    '''下面的教学示意说明：像素平均误差接近时，结构质量仍可能明显不同。示例中的结构分数是简化代理，不是标准 S-measure 实现：''',
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    '#| fig-cap: "COD 评价指标互补性示意：两个预测的 MAE 相近，但预测 A 在边界区域错误集中（结构性差），预测 B 误差均匀分散。S-measure 会对 A 给出更低评分——这说明多指标联合评价的必要性。"',
    '#| fig-cap: "固定种子教学示意：两个预测的 MAE 分别约为 0.155 和 0.175，而简化结构代理对边界缺失更敏感。该代理不等于标准 S-measure；图仅说明平均像素误差与结构质量可能给出不同判断。"',
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "# Simple proxy for S-measure: mean of object-region IoU and edge-region F1",
    "# Teaching-only structure proxy: mean of region IoU and edge F1; not S-measure",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "def simple_sm(pred, gt, thresh=0.5):",
    "def structure_proxy(pred, gt, thresh=0.5):",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "sm_a = simple_sm(pred_a, gt)\nsm_b = simple_sm(pred_b, gt)",
    "sp_a = structure_proxy(pred_a, gt)\nsp_b = structure_proxy(pred_b, gt)",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "f'Pred A (boundary miss)\\nMAE={mae_a:.3f}  Sm≈{sm_a:.3f}',\n         f'Pred B (diffuse noise)\\nMAE={mae_b:.3f}  Sm≈{sm_b:.3f}'",
    "f'Pred A (boundary miss)\\nMAE={mae_a:.3f}  Struct≈{sp_a:.3f}',\n         f'Pred B (diffuse noise)\\nMAE={mae_b:.3f}  Struct≈{sp_b:.3f}'",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "plt.suptitle('Multiple metrics needed: MAE≈same but Sm differs (boundary quality matters)',",
    "plt.suptitle('MAE can be close while a teaching structure proxy differs',",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "规模与划分以原始论文为准，部分数字待平台核实后更新。",
    "本表只列当前可从论文或官方项目页核对规模的条目；仍处于 metadata-only 且规模未核的资源只在 Research Catalog 中保留。",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "| COD10K[@fan2020sinet] | 5,066 伪装（~10K 总） | 3,040 训 / 2,026 测 | 69 类 / 78 子类；当前最大图像基准 |",
    "| COD10K[@fan2020sinet] | 5,066 伪装（约 10K 总） | 3,040 训 / 2,026 测 | 类别覆盖较广的常用图像基准 |",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "| NC4K[@lyu2021ranknet] | 4,121 | 仅测试 | 跨数据集泛化评测标准 |",
    "| NC4K[@lyu2021ranknet] | 4,121 | 仅测试 | 常用外部测试与排序标注资源 |",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "| MCOD | 多光谱 COD | — | 首个多光谱伪装基准[@mcod2025] |\n| MM-CamObj | 多模态 | — | MLLM 问答评测[@mmcamobj2024] |\n| PlantCamo[@plantcamo2025] | 农业/植物 | — | 植物伪装，跨域应用 |",
    "| PlantCamo[@plantcamo2025] | 农业/植物 | 1,250 图像、58 类 | 植物伪装，跨域应用 |",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "| MoCA-Mask[@cheng2022implicit] | 87 序列 (71 训 / 16 测) | 移动伪装动物（源自 MoCA[@lamdouar2020moca]）；最常用视频基准 |",
    "| MoCA-Mask[@cheng2022implicit] | 87 序列（71 训 / 16 测；22,939 帧） | 移动伪装动物（源自 MoCA[@lamdouar2020moca]）；常用视频基准 |",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "| CamoVid60K[@vu2026camovid] | ~60K 帧 | 大规模；用于预训练/增强 |",
    "| CamoVid60K[@vu2026camovid] | 218 视频、62,774 标注帧 | 较大规模视频理解资源 |",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "| MSVCOD[@gao2025msvcod] | — | 多场景视频，难度多样 |",
    "| MSVCOD[@gao2025msvcod] | 162 clips、9,486 帧 | 多场景视频；当前元数据仍待独立许可核验 |",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    ": COD 数据集全景（与 data/datasets.yaml 同源；— 表示规模待核实；详见附录 A） {#tbl-datasets}",
    ": COD 数据集全景（规模来自论文或官方项目页；许可与核验状态详见附录 A 和 Research Catalog） {#tbl-datasets}",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "多光谱和多模态数据集把第 9 章的信道选择权引入智能检测",
    "多光谱和多模态资源把第 9 章的信道选择权引入智能检测；MCOD 与 MM-CamObj 当前仍以 metadata-only 方式保留在 Catalog，待规模和协议完成独立核验后再进入正式数量表",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "CAMO 首次系统推动像素级 COD；COD10K 把类别和样本规模显著扩大，成为主训练集；NC4K 主要承担跨数据集泛化测试",
    "CAMO 较早推动像素级 COD；COD10K 扩大了类别与样本规模，成为常见训练资源；NC4K 常用于外部测试和排序研究",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "MCOD 和 MM-CamObj 则把第 9 章的多模态思想引入智能识别。",
    "MCOD 和 MM-CamObj 则提示多光谱与多模态评价方向，但其正式数量与协议仍按 Catalog 核验状态解释。",
)
replace(
    "book/chapters/10-intelligent-overview-datasets.qmd",
    "是目前标注质量最高的图像 COD 基准之一",
    "提供了较系统的标注与类别信息；其边界质量、版本和不确定区域仍应按具体发布包审计",
)

# 5. Explicit section numbering for stable @sec cross-references.
replace(
    "book/_quarto.yml",
    "bibliography: references.bib\n\nexecute:",
    "bibliography: references.bib\nnumber-sections: true\n\nexecute:",
)

# 6. Record review disposition for future audits.
response = ROOT / "docs/BOOK_REVIEW_RESPONSE_20260713.md"
response.write_text(
    '''# Claude 专著审校意见处理记录（2026-07-13）\n\n"
    "来源：`BOOK_REVIEW_20260713.md`。本记录按 PR #13 的 21 章结构复核，不机械沿用旧 16 章行号。\n\n"
    "## 已采纳并落实\n\n"
    "- 压缩第6、9章小结，删除口号式尾句；删除第14章进入评价篇前的重复口号。\n"
    "- 将 `flowcamo`、`dualvcod`、`coder` 统一表述为作者研究议程，不再与已发表方法等量齐观。\n"
    "- 删除“计划中提到的 SCODE”与开发对话式口吻；将 Demo 路线降为教学证据说明。\n"
    "- 修正第2章 `@sec-` 交叉引用，并在 `_quarto.yml` 显式启用章节编号。\n"
    "- 将 PFNet 的 `prohibition` 误植改为“干扰挖掘与背景抑制”。\n"
    "- 第11章导读补入11.8，并将 `coder` 标为研究议程。\n"
    "- 第10章数据表补齐 PlantCamo、MoCA-Mask、CamoVid60K、MSVCOD 的可核规模；MCOD/MM-CamObj 留在 metadata-only Catalog，暂不进入数量表。\n"
    "- 图8格拉姆图 caption 降格为固定种子教学代理；图10不再把简化结构代理称为 S-measure，并写明固定种子结果。\n\n"
    "## 已由评价篇重构消解\n\n"
    "- 旧第15章“与用户此前提出的……”段落已在第15章整体重写时删除。\n"
    "- 旧第16章主动感知图及“单调提升”caption 已随旧章节删除；新第21章不含该图。\n"
    "- 新第15章导读已覆盖15.0和全章分工。\n\n"
    "## 仍属出版前 QA\n\n"
    "- HTML/ePub 已由 CI 构建；PDF 仍需中文字体、宽表、公式和交叉引用的独立校样。\n"
    "- 所有代码图在正式发行前继续逐图核对随机种子、caption和实际数值。\n"
    "- 数据集许可与 metadata-only 条目仍按 Research Catalog 和附录的核验状态管理。\n'''.replace('"\n    "', ''),
    encoding="utf-8",
)

print("Applied Claude book review remediation.")
