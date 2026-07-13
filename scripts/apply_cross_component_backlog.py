#!/usr/bin/env python3
"""One-shot cross-component remediation discovered during the Awesome audit."""

from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    left = text.find(start)
    if left < 0:
        raise SystemExit(f"start marker not found: {start}")
    right = text.find(end, left)
    if right < 0:
        raise SystemExit(f"end marker not found: {end}")
    return text[:left] + replacement.rstrip() + "\n\n" + text[right:]


APPENDIX = dedent(
    r'''
    ---
    title: "附录：数据、指标、术语与出版说明"
    subtitle: "Appendix: Datasets, Metrics, Terminology, and Publication Notes"
    bibliography: ../references.bib
    ---

    ## A　精选资源、完整目录与数据集登记 {#sec-a}

    CamoGED 将资源维护分为三个互不替代的层级：

    1. **Awesome Camouflage** 是人工精选的阅读地图，只展示 `curated: true` 且具有编辑说明的条目；
    2. **CamoGED Research Catalog** 是完整的已接受元数据目录，允许收录 `metadata-only` 条目，但不因此背书其方法结论、许可证或复现状态；
    3. **本书参考文献** 只包含正文实际引用且经编辑复核的来源。Catalog 新增条目不会自动进入书稿。

    自动发现流程只生成候选报告和 GitHub triage issue；它无权直接修改已接受目录，也无权改写本书。候选必须经过人工筛选和 Draft PR 才能成为 Catalog 记录，之后还需独立编辑决定是否进入 Awesome 精选层。

    | 字段组 | 关键字段 | 用途 |
    |---|---|---|
    | 资源身份 | `resource_type`, `canonical_url`, `publication_status` | 区分论文、综述、专著、标准、历史资料和项目页，并关联规范来源 |
    | 任务轴 | `tasks[]` | 图像/视频 COD、实例、bbox、跟踪、指代、协同、开放词汇、生成、评价等 |
    | 模态轴 | `modalities[]` | RGB、视频、深度、热红外、多/高光谱、偏振、多模态和视觉语言 |
    | 监督轴 | `supervision[]` | 全监督、弱监督、半监督、无监督、零样本、提示式、训练自由等 |
    | 方法与语境 | `method_families[]`, `contexts[]` | 区分架构路线及生物、军事、艺术设计、计算机视觉等知识语境 |
    | 证据等级 | `verification_status`, `last_verified`, `verified_by` | `metadata-only` 仅表示身份与来源已核，不表示结论或结果已复核 |
    | 策展状态 | `curated`, `curation_tier`, `date_added` | 控制精选层、核心阅读和完整目录之间的关系 |
    | 许可状态 | `license_status`, `license` | 许可证不明时禁止由 CamoGED 再分发文件 |

    数据集登记仍由 `data/datasets.yaml` 维护。正式使用时至少核查名称、任务、模态、规模、划分、标注粒度、官方来源、许可证状态、发布状态和最后核验日期。项目只提供导航和校验信息，不重新分发许可不明或受限数据。

    网站 `/awesome` 提供精选阅读地图，`/catalog` 提供可筛选完整目录，`/datasets` 提供数据集导航，`/updates` 显示人工审核日期与最近一次自动扫描状态。第 10 章给出较稳定的任务版图，不复制会快速过期的完整列表。

    ## B　指标速查 {#sec-b}

    | 层级 | 典型指标 | 方向 | 主要问题 | 不能替代什么 |
    |---|---|:---:|---|---|
    | 像素/前景图 | MAE、$F_\beta^w$ | ↓ / ↑ | 整体误差、漏检与误报 | 结构、实例和时间 |
    | 结构 | $S_\alpha$、$E_\phi$ | ↑ | 形状与区域一致性 | 标准 Boundary IoU；未对标实现不得借名 |
    | 实例 | AP、AR、Mask AP | ↑ | 是否分清多个目标 | ID 与轨迹 |
    | 视频 | $\mathcal J$、$\mathcal F$、$\mathcal J\&\mathcal F$ | ↑ | 区域与边界 | 时间稳定性；后者应另报 |
    | 生成 | FID/KID、LPIPS、SSIM | ↓/↑ | 分布或感知真实性 | 伪装/攻击有效性 |
    | 对抗 | ASR、AP drop、迁移率 | ↑ | 特定观察者是否被误导 | 人类自然性、物理鲁棒性 |
    | 人因 | 反应时、hit/miss、$d'$ | 依定义 | 观察者敏感性与偏置 | 机器分割质量 |
    | 物理信号 | 热对比、SCR、光谱角 | 依定义 | 特定传感器信号差异 | 跨传感器任务结果 |

    指标首次出现必须注明实现、版本、阈值、方向和聚合方式。视频、物理和人因实验还应报告方差、置信区间或重复次数。实验性替代指标必须使用描述性名称或 `_lite` 后缀，不能占用标准名称。

    ## C　统一报告模板 {#sec-c}

    本书采用：

    $$
    \mathcal E=\langle O,X,T,P,M\rangle,
    $$

    其中 $O$ 为观察者，$X$ 为输入/观测信道，$T$ 为任务，$P$ 为协议，$M$ 为指标集合。文本提示、人工框和交互次数属于任务输入或协议条件，不应被伪装成模型自动能力。

    一个最小机器评测 manifest：

    ```yaml
    name: cod-mask-example
    observer: model-name-and-version
    channel: RGB image
    task: camouflaged object segmentation
    protocol: fixed test split; automatic prediction; no manual prompt
    metrics: [mae, fw, sm, em, f]
    implementation_version: camo-eval-x.y.z
    threshold_policy: continuous maps for COD core metrics
    uncertainty: bootstrap 95% CI
    last_verified: 2026-07-13
    ```

    若额外报告 `boundary_match_score` 等实验性描述量，必须单列实现 ID 和定义，不能称为标准 Boundary IoU。

    ## D　术语中英对照 {#sec-d}

    - **hider / seeker / evaluator**：隐藏方／揭示方／评价者；跨域总称。
    - **crypsis / concealment**：以降低察觉概率为目标的隐蔽。
    - **masquerade**：目标被察觉但被当作无关对象的伪装性拟态。
    - **mimicry**：信号或外观对另一模型对象的拟态，范围不等同于伪装。
    - **disruptive coloration**：瓦解色；通过竞争边缘和轮廓破坏降低整体组织。
    - **countershading**：消影；以体表明暗抵消部分形状阴影线索。
    - **stealth / low observable**：隐身／低可探测；需说明具体信道和任务。
    - **COD / VCOD / CIS / RCOD / COT**：像素级伪装分割／视频 COD／实例分割／bbox 型现实 COD／伪装目标跟踪。
    - **adversarial camouflage**：针对机器观察者优化的对抗伪装；不自动等于对人隐蔽。

    ## E　检索、核验与证据等级 {#sec-e}

    检索数据库、关键词、纳入标准与截止日期见 `docs/BOOK_SEARCH_METHODOLOGY.md`；逐项事实问题见 `docs/BOOK_FACTCHECK_REGISTER.md`。正文使用三类主要证据：P 级一手论文、标准与档案；S 级权威专著与综述；T 级预印本、项目页与临时资料。关键历史事实和“首个/最大/最新”结论至少需要一条 P 级证据，并在每次发布前重新检索。

    Catalog 的 `metadata-only` 状态不等同于本书的 P 级证据。自动发现可以提示新来源，但不能自动改变正文结论。

    ## F　代码、项目与动态资源 {#sec-f}

    - 书稿源码：`book/`
    - 人工精选资源：`awesome/README.md` 与网站 `/awesome`
    - 完整研究目录：`data/papers.yaml` 与网站 `/catalog`
    - 数据集元数据：`data/datasets.yaml` 与网站 `/datasets`
    - 已核验结果：`data/leaderboard.yaml` 与网站 `/leaderboard`
    - 自动更新状态：网站 `/updates` 与 GitHub `awesome:triage` issues
    - 评价工具与验证登记：`camo-eval/`、`camo-eval/VALIDATION.md`
    - 浏览器教学演示：网站 `/demo`
    - 未发表作者项目：`projects/coder`、`projects/flowcamo`、`projects/dualvcod`

    未发表项目在正文中只作为研究议程，不作为已完成原创贡献。动态网站可以展示开发状态，但正式书稿不得预填结果；Demo 也不得因某项资源进入 Catalog 就自动接入其模型或数据。

    ## G　图像版权与版本清单 {#sec-g}

    正式发布前，每幅外部图像应登记：文件名、标题、作者/机构、原始链接、年份、许可、是否改绘、署名文字和核验日期。无法确认许可的历史图、艺术作品、军事照片和动物摄影不得直接进入发行版；优先使用公版、开放许可、作者授权或原创示意图。

    本版版本日期：**2026-07-13**。引用元数据见仓库根目录 `CITATION.cff`；正文采用 CC BY 4.0，代码采用 Apache-2.0，数据集遵循各自上游许可。
    '''
).strip()


CH10_SECTION = dedent(
    r'''
    ## 10.2 任务、监督与模态三轴谱系 {#sec-10-taxonomy}

    COD 已不再是从“单图二值分割”线性升级到“开放词汇”的单一阶梯。更准确的组织方式，是把**任务输出、监督条件和观测模态**视为三条正交轴：同一项工作可以同时属于视频、零样本、视觉语言和实例任务；数据集则是承载这些组合的资源，而不是天然属于“评价”一类。

    ::: {.callout-note}
    ## 动态边界
    本节是截至 **2026-07-13** 的编辑快照。网站 Research Catalog 负责持续发现和多轴筛选；自动候选不会直接改写本章，新增分支只有经过一手来源核验和书稿审阅后才进入正文。
    :::

    ### 10.2.1 任务轴：模型究竟要输出什么

    | 任务分支 | 主要输入 | 主要输出 | 代表性资源 | 关键评价问题 |
    |---|---|---|---|---|
    | 图像 COD | 单张图像 | 二值掩膜 | COD10K、CAMO、NC4K[@fan2020sinet] | 区域、结构和边界 |
    | 视频 COD | 视频序列 | 时序掩膜 | MoCA-Mask、CamoVid60K[@cheng2022implicit; @vu2026camovid] | 单帧质量、边界和时间稳定性 |
    | 伪装实例分割 | 单图/视频 | 每实例掩膜 | COD10K 实例标注等[@xiao2024survey] | 实例分离、遮挡和 Mask AP |
    | bbox 型 RCOD | 单张图像 | 类别与边界框 | 三个由分割集转换的检测基准[@rcod2025] | 定位、分类、AP 与效率 |
    | 伪装目标跟踪 | 初始框/目标 + 视频 | 连续边界框或轨迹 | COTD（200 序列、约 8 万帧）[@cotd2024] | 初始化、漂移、遮挡恢复和在线约束 |
    | 指代 COD | 图像 + 自然语言 | 被描述目标的掩膜 | R2C7K[@zhang2023refcod] | 文本是否指向正确实例 |
    | 协同 COD | 相关图像组 | 多图共有目标掩膜 | CoCOD8K[@zhang2023collaborative] | 跨图共同性与单图伪响应 |
    | 开放词汇分割/检测 | 图像 + 类别或细粒度文本 | 未见类别掩膜或框 | OVCamo、OVCOD-D[@ovcamo2023; @sddf2026] | 基类/新类泛化、文本特异性和定位 |
    | 视觉语言理解 | 图像/视频 + 问题 | 回答、解释、定位或复合输出 | MM-CamObj、MMCSBench[@mmcamobj2024; @mmcsbench2025] | 幻觉、语义正确性与空间证据 |
    | 鲁棒性与退化评测 | 干净/退化输入 | 分条件性能曲线 | COD10K-C 等预印本基准[@cod10kc2026] | 腐蚀类型、严重度、最坏条件和不确定性 |

    这些任务不能用同一组数字统治。bbox AP 不能替代掩膜质量，$\mathcal J\&\mathcal F$ 不能替代跟踪漂移，语言回答正确也不能证明像素定位正确。任务定义必须先于模型比较。

    ### 10.2.2 监督轴：模型得到多少人工信息

    - **全监督**仍是标准图像/视频 COD 的主流基线，依赖像素掩膜或实例标注。
    - **弱监督**以点、框、涂鸦、图像级标签或文本替代完整掩膜；必须把提示成本计入协议。
    - **半监督**同时使用少量标注与大量未标注数据，例如 SCOUT 将自适应数据选择与文本交互结合[@scout2025]。
    - **无监督/自监督**依赖预训练特征、聚类或动态伪标签，例如 UCOD-DPL 的教师—学生伪标签更新[@ucoddpl2025]。
    - **零样本/训练自由**要求不使用伪装像素标注，可能借助 MLLM、CLIP、SAM/SAM2 或其他通用底座；CaMF 是代表性路线之一[@camf2025]。

    “标注更少”不自动意味着协议更强。若方法使用外部分割集、人工文本、交互点、专有大模型或测试时人工选择，这些都属于额外监督和资源，应与纯零样本或全自动方法分档报告。

    ### 10.2.3 模态轴：观察者看见什么

    COD 研究已从 RGB 扩展到视频运动、深度、热红外、多/高光谱、偏振、多模态和视觉语言输入。模态扩展改变的是观测信道 $X$：深度或热信号可能打破可见光伪装，但会引入配准、传感器噪声和缺失信道问题；视觉语言输入增加语义能力，也带来文本敏感性和幻觉风险。不同模态结果不能只按同名任务合并排名。

    三条轴共同决定实验协议。一个“视频零样本视觉语言跟踪器”和一个“全监督 RGB 图像分割器”都可以研究伪装，但它们没有直接可比的单一排行榜。第 11 章聚焦图像分割结构，第 12 章处理视频与时间，第 13 章处理实例及扩展任务，第 14 章讨论基础模型、开放词汇和视觉语言；完整组合由动态 Catalog 维护。
    '''
).strip()


SAM_RECENT = dedent(
    r'''
    ### 14.2.3 2025—2026：从能力评测到提示、特征与记忆适配 {#sec-sam2-recent}

    近期工作显示，“把 SAM2 用于 VCOD”至少包含三类不同问题，不能都归为同一种适配。第一类是**系统评测与适配基线**：对不同提示、数据集和冻结策略进行对照，明确 SAM2 在伪装视频中的能力边界[@samvcos2025]。第二类是**自动提示生成**：CamoSAM2 由运动—外观线索产生和精炼提示，重点解决全自动初始化，而不是依赖人工点击[@camosam2_2025]。第三类是**特征与记忆适配**：CamSAM2 引入 decamouflaged token、当前/历史帧对象感知融合和对象原型记忆，在不改写 SAM2 主体参数的前提下增强伪装视频表征[@camsam2_2025]。

    这三类路线的比较必须固定提示来源。人工点、真实首帧 mask、外部检测器生成框和完全自动提示的难度不同；若不报告提示数量、失败重试、是否使用未来帧和人工筛选，所谓“SAM2 提升”没有可解释性。视频基础模型的核心不只是分割器多强，而是**谁发现目标、如何初始化、错误如何被记忆传播以及何时纠错**。

    本节列举的是截至 2026-07-13 的代表性快照。更多预印本和后续版本由 Research Catalog 动态维护；Catalog 收录不等于书稿已接受其结论。
    '''
).strip()


OPEN_VOCAB = dedent(
    r'''
    开放词汇路线也已经从“用 CLIP 提供粗语义”发展为任务和数据集本身的重新定义。OVCamo 将开放词汇伪装分割作为独立任务，提供类别语义、结构和像素掩膜[@ovcamo2023]；2026 年预印本 SDDF 则把细粒度文本特异性用于开放词汇 bbox 检测，并构建 OVCOD-D[@sddf2026]。二者分别回答“未见类别的像素分割”和“文本驱动的开放集定位”，不能只因都使用视觉语言模型而合并评价。

    这类方法必须报告文本来源、模板、同义词扩展、是否由 MLLM 自动生成描述，以及基类/新类划分。文本提示是协议输入，不是免费的模型能力。
    '''
).strip()


MLLM_RECENT = dedent(
    r'''
    NeurIPS 2025 的 MMCSBench 进一步把评测扩展为 22,537 张图像和 76,843 个图文对，覆盖五类细粒度伪装任务，并单列 Camouflage Efficacy Assessment[@mmcsbench2025]。其价值在于揭示 LVLM 的场景理解和推理缺口，而不是替代像素分割基准。MM-CamObj、MMCSBench 与传统 mask 数据集应形成并行评价：前两者检查语言与机制理解，后者检查空间边界。
    '''
).strip()


BIB_ENTRIES = dedent(
    r'''

    @article{rcod2025,
      title   = {Toward Realistic Camouflaged Object Detection: Benchmarks and Method},
      author  = {Xin, Zhimeng and Wu, Tianxu and Chen, Shiming and Ye, Shuo and Xie, Zijing and Zou, Yixiong and You, Xinge and Guo, Yufei},
      journal = {arXiv preprint arXiv:2501.07297},
      year    = {2025},
      url     = {https://arxiv.org/abs/2501.07297}
    }

    @article{cotd2024,
      title   = {Camouflaged Object Tracking: A Benchmark},
      author  = {Guo, Xiaoyu and Zhong, Pengzhi and Zhang, Hao and Huang, Defeng and Shao, Huikai and Zhao, Qijun and Li, Shuiwang},
      journal = {arXiv preprint arXiv:2408.13877},
      year    = {2024},
      url     = {https://arxiv.org/abs/2408.13877}
    }

    @article{scout2025,
      title   = {{SCOUT}: Semi-supervised Camouflaged Object Detection by Utilizing Text and Adaptive Data Selection},
      author  = {Yan, Weiqi and Chen, Lvhai and Zhang, Shengchuan and Zhang, Yan and Cao, Liujuan},
      journal = {arXiv preprint arXiv:2508.17843},
      year    = {2025},
      url     = {https://arxiv.org/abs/2508.17843}
    }

    @article{ucoddpl2025,
      title   = {{UCOD-DPL}: Unsupervised Camouflaged Object Detection via Dynamic Pseudo-label Learning},
      author  = {Yan, Weiqi and Chen, Lvhai and Kou, Huaijia and Zhang, Shengchuan and Zhang, Yan and Cao, Liujuan},
      journal = {arXiv preprint arXiv:2506.07087},
      year    = {2025},
      url     = {https://arxiv.org/abs/2506.07087}
    }

    @article{camf2025,
      title   = {Towards Real Zero-Shot Camouflaged Object Segmentation without Camouflaged Annotations},
      author  = {Lei, Cheng and Fan, Jie and Li, Xinran and Xiang, Tian-Zhu and Li, Ao and Zhu, Ce and Zhang, Le},
      journal = {arXiv preprint arXiv:2410.16953},
      year    = {2024},
      url     = {https://arxiv.org/abs/2410.16953}
    }

    @article{ovcamo2023,
      title   = {Open-Vocabulary Camouflaged Object Segmentation},
      author  = {Pang, Youwei and Zhao, Xiaoqi and Zuo, Jiaming and Zhang, Lihe and Lu, Huchuan},
      journal = {arXiv preprint arXiv:2311.11241},
      year    = {2023},
      url     = {https://arxiv.org/abs/2311.11241}
    }

    @article{camsam2_2025,
      title   = {{CamSAM2}: Segment Anything Accurately in Camouflaged Videos},
      author  = {Zhou, Yuli and Sun, Guolei and Li, Yawei and Fu, Yuqian and Benini, Luca and Konukoglu, Ender},
      journal = {arXiv preprint arXiv:2503.19730},
      year    = {2025},
      url     = {https://arxiv.org/abs/2503.19730}
    }

    @inproceedings{mmcsbench2025,
      title     = {{MMCSBench}: A Fine-Grained Benchmark for Large Vision-Language Models in Camouflage Scenes},
      author    = {Zhang, Jin and Zhang, Ruiheng and Cao, Zhe and Chen, Kaizheng},
      booktitle = {Advances in Neural Information Processing Systems},
      year      = {2025},
      url       = {https://neurips.cc/virtual/2025/poster/121542}
    }

    @article{sddf2026,
      title   = {{SDDF}: Specificity-Driven Dynamic Focusing for Open-Vocabulary Camouflaged Object Detection},
      author  = {Liang, Jiaming and Zhan, Yifeng and Liu, Chunlin and Zheng, Weihua and Peng, Bingye and Liang, Qiwei and Cai, Boyang and Mai, Xiaochun and Nie, Qiang},
      journal = {arXiv preprint arXiv:2603.26109},
      year    = {2026},
      url     = {https://arxiv.org/abs/2603.26109}
    }

    @article{cod10kc2026,
      title   = {{COD10K-C}: Benchmarking Robustness of Camouflaged Object Detection Under Natural Image Corruptions},
      author  = {Sayem, Arafat Hossain},
      journal = {arXiv preprint arXiv:2606.02603},
      year    = {2026},
      url     = {https://arxiv.org/abs/2606.02603}
    }
    '''
).strip()


def update_book() -> None:
    write("book/chapters/appendix-resources.qmd", APPENDIX)

    ch10_path = "book/chapters/10-intelligent-overview-datasets.qmd"
    ch10 = read(ch10_path)
    ch10 = ch10.replace(
        "10.2 节展开任务谱系（从图像到视频到开放词汇）",
        "10.2 节以任务、监督和模态三轴重建领域谱系",
    )
    ch10 = replace_between(ch10, "## 10.2 ", "## 10.3 ", CH10_SECTION)
    ch10 = ch10.replace(
        "@tbl-datasets 给出主要数据集的综合概览，按任务/模态组织，与 `data/datasets.yaml` 同源。规模与划分以原始论文为准，部分数字待平台核实后更新。",
        "@tbl-datasets 是与 `data/datasets.yaml` 和 Research Catalog 对齐的编辑快照，而不是自动复制的完整目录。规模、划分与发布状态以一手来源为准；表中条目在未单独说明时均只达到 `metadata-only`，不代表许可证或方法结论已完整核验。",
    )
    ch10 = ch10.replace("当前最大图像基准", "主流大规模图像基准")
    ch10 = ch10.replace("跨数据集泛化评测标准", "常用跨数据集泛化测试")
    start = "**扩展/专项图像任务**"
    end = "**视频 COD**"
    extension = dedent(
        r'''
        **扩展/专项任务**

        | 数据集/基准 | 任务 | 规模 | 注 |
        |---|---|---:|---|
        | CoCOD8K[@zhang2023collaborative] | 协同 COD | ~8K 图像 | 多图共有目标 |
        | R2C7K[@zhang2023refcod] | 指代 COD | ~7K 图像 | 自然语言引导 |
        | RCOD converted benchmarks[@rcod2025] | bbox 型 RCOD | 3 个转换基准 | 从现有分割数据补充检测框标注 |
        | OVCamo[@ovcamo2023] | 开放词汇分割 | 11,483 图像 | 类别语义、结构与像素标注 |
        | MM-CamObj[@mmcamobj2024] | 多模态问答 | 以官方发布为准 | 伪装场景 LVLM 评价 |
        | MMCSBench[@mmcsbench2025] | 视觉语言理解/评价 | 22,537 图像；76,843 图文对 | 五类细粒度任务，含伪装效能评价 |
        | MCOD[@mcod2025] | 多光谱 COD | 以官方发布为准 | 多光谱基准；新颖性主张归于原文 |
        | PlantCamo[@plantcamo2025] | 农业/植物 | 1,250 图像 | 58 类植物伪装目标 |
        | ACOD-12K[@wang2024depth] | RGB-D 农业 COD | ~12K 图像 | 深度辅助的隐蔽作物检测 |
        '''
    ).strip()
    ch10 = replace_between(ch10, start, end, extension)
    ch10 = ch10.replace(
        "| MSVCOD[@gao2025msvcod] | — | 多场景视频，难度多样 |",
        "| MSVCOD[@gao2025msvcod] | 162 片段 / 9,486 帧（按预印本） | 多场景视频；发布状态需动态核查 |\n| COTD[@cotd2024] | 200 序列 / 约 80,000 帧 | bbox 跟踪基准，区别于像素级 VCOD |",
    )
    ch10 = ch10.replace(
        ": COD 数据集全景（与 data/datasets.yaml 同源；— 表示规模待核实；详见附录 A） {#tbl-datasets}",
        ": COD 数据集与任务资源快照（完整状态、许可和更新见 Research Catalog；详见附录 A） {#tbl-datasets}",
    )
    ch10 = ch10.replace(
        "附录 A 和 `/datasets` 页面应把这些角色写清楚",
        "附录 A、`/catalog` 与 `/datasets` 页面应把这些角色写清楚",
    )
    write(ch10_path, ch10)

    ch14_path = "book/chapters/14-foundation-models.qmd"
    ch14 = read(ch14_path)
    guide_end = ":::"
    first = ch14.find(guide_end, ch14.find("::: {.callout-tip}"))
    if first < 0:
        raise SystemExit("chapter 14 guide callout end not found")
    insertion = dedent(
        r'''

        ::: {.callout-note}
        本章前沿文献快照核验至 **2026-07-13**。Research Catalog 负责持续发现候选；只有正文实际采用且经一手来源复核的工作才进入本章与 `references.bib`。
        :::
        '''
    )
    ch14 = ch14[: first + len(guide_end)] + insertion + ch14[first + len(guide_end) :]
    ch14 = ch14.replace("## 14.3 CLIP", SAM_RECENT + "\n\n## 14.3 CLIP", 1)
    ch14 = ch14.replace("## 14.4 DINOv2", OPEN_VOCAB + "\n\n## 14.4 DINOv2", 1)
    mm_sentence = "**MM-CamObj** 是专门为评测 MLLM 在伪装场景能力而构建的数据集，提供多模态问答标注[@mmcamobj2024]。它允许评测\"模型是否真正理解了伪装机制\"——比如是否能识别背景匹配、轮廓瓦解、拟态等具体机制。"
    if mm_sentence not in ch14:
        raise SystemExit("MM-CamObj insertion marker not found")
    ch14 = ch14.replace(mm_sentence, mm_sentence + "\n\n" + MLLM_RECENT, 1)
    old_cross = dedent(
        r'''
        基础模型对 COD 的另一个贡献，是**跨域迁移的显著改善**。第 10.6 节列出了医学影像（息肉）、工业质检（细微缺陷）、农业（PlantCamo[@plantcamo2025]）等共享"目标-背景高相似度"结构的应用域。使用基础模型骨干的 COD 方法，从"野生动物伪装"迁移到"医学息肉分割"的性能保留率，普遍高于使用专有 CNN 骨干的方法——因为基础模型的特征空间更通用，"高相似度区域的结构特征"在跨域后仍有一定的可迁移性。

        这一红利背后的原因，正是基础模型训练数据的多样性：自然图像、医学图像、工业图像在大规模预训练集中均有覆盖（尽管比例差异很大），使模型已经对多种视觉统计分布有基础认识，而不是只"看过"自然场景。跨域迁移能力的提升，是"通用底座"优于"专用模型"的最直接实证[@xiao2024survey]。
        '''
    ).strip()
    new_cross = dedent(
        r'''
        基础模型对 COD 的潜在贡献之一，是降低跨域适配的起点成本。第 10.6 节列出的医学、工业和农业任务共享低对比、弱边界和目标—背景相似等结构，但目前没有足够统一证据支持“基础模型跨域性能普遍高于专用 CNN”这一泛化结论。不同底座的预训练语料、提示方式、解码器和目标域标注预算差异很大，必须在相同协议下实证比较。

        因此，跨域红利应被当作**待检验假设**：通用预训练可能提供对象性、边界和语义先验，也可能因训练数据偏向显著目标而忽略伪装线索。研究者应报告零样本、少样本和全监督三档结果，并明确预训练数据与目标域是否重叠；不能假设医学或工业图像必然被某个基础模型充分覆盖[@xiao2024survey]。
        '''
    ).strip()
    if old_cross not in ch14:
        raise SystemExit("chapter 14 cross-domain marker not found")
    ch14 = ch14.replace(old_cross, new_cross, 1)
    write(ch14_path, ch14)

    refs_path = "book/references.bib"
    refs = read(refs_path).rstrip()
    for block in BIB_ENTRIES.split("\n\n@"):
        block = block if block.startswith("@") else "@" + block
        key_match = re.match(r"@\w+\{([^,]+),", block)
        if not key_match:
            continue
        key = key_match.group(1)
        if f"{{{key}," not in refs:
            refs += "\n\n" + block.strip()
    write(refs_path, refs)


def update_factcheck_and_methodology() -> None:
    path = "docs/BOOK_FACTCHECK_REGISTER.md"
    text = read(path)
    text = text.replace(
        "| F12 | 数据表 | `—`、预印本、未核许可证混入正文 | 附录增加核验字段和正式表准入规则 | OPEN | 仅渲染 verified 条目 |",
        "| F12 | 数据表 | `—`、预印本、未核许可证混入正文 | 改为精选书稿快照 + Catalog 状态字段；`metadata-only` 不冒充完整核验 | REVISED | 发布前复核表内数字、状态和许可证 |",
    )
    marker = "| F14 | 图像版权 | 缺少逐图来源与许可台账 | 纳入附录与体例要求 | OPEN | 发布前逐图清账 |"
    additions = dedent(
        r'''
        | F15 | 全书动态断言 | “首个/最大/最新”可能被自动发现的新文献推翻 | 增加 Catalog/书稿隔离和发布前重新检索规则 | REVISED | 每次发布更新检索日期与受影响断言 |
        | F16 | 第10章 | 任务谱系遗漏 bbox、跟踪、不完整监督、零样本、VLM 与鲁棒性 | 重构为任务/监督/模态三轴，并加入代表性一手来源 | VERIFIED | 季度检查新增任务分支 |
        | F17 | 第14章 | 2025—2026 SAM2、开放词汇和 LVLM 文献缺失 | 补 CamSAM2、MMCSBench、SDDF 等，并明确快照边界 | VERIFIED | 预印本转正式出版时更新书目 |
        | F18 | 第14章跨域 | “基础模型跨域性能普遍高于专用 CNN”缺乏统一实证 | 改为待检验假设，要求零/少/全监督同协议比较 | REVISED | 有跨域基准证据后再作强结论 |
        | F19 | Demo | Catalog 收录可能被误解为可自动接入模型或已复现 | Demo 增加本地处理、指标边界和模型准入门槛 | VERIFIED | 接入真实模型时重新安全与许可审查 |
        '''
    ).strip()
    if additions not in text:
        if marker not in text:
            raise SystemExit("factcheck marker not found")
        text = text.replace(marker, marker + "\n" + additions, 1)
    write(path, text)

    methodology_path = "docs/BOOK_SEARCH_METHODOLOGY.md"
    methodology = read(methodology_path)
    dynamic = dedent(
        r'''

        ## 与动态 Catalog 的关系

        Awesome 自动发现每周从 arXiv 与 Crossref 生成候选报告，但候选只能作为检索线索。自动流程不得直接修改书稿、事实核查状态或参考文献。编辑在准备新版本时应：

        1. 检查自上次 `coverage_through` 之后的 triage issues；
        2. 对影响“首个、最大、最新、主要基准”等表述的候选回查一手来源；
        3. 记录哪些结论被保留、降格或删除；
        4. 只把正文实际引用的来源加入 `book/references.bib`。
        '''
    ).rstrip()
    if "## 与动态 Catalog 的关系" not in methodology:
        methodology = methodology.replace("## 当前核验日期", dynamic + "\n\n## 当前核验日期")
    write(methodology_path, methodology)


def update_demo_and_readme() -> None:
    demo = dedent(
        r'''
        ---
        pageClass: camoged-demo-page
        ---

        <CamoDemo />

        ## 使用边界与数据处理

        - 合成场景由浏览器确定性生成；用户选择的本地图像只在当前浏览器内解码和处理，页面不会把图像上传到 CamoGED 服务器。
        - “seeded colour region”、画笔掩膜、直方图重叠和亮度差都是教学操作或探索性描述量，不是 COD 模型推理，也不是标准伪装难度分数。
        - 页面结果不能用于论文排行榜、人类可探测性、生态适应度、对抗成功率或任务效能结论。正式研究应使用声明观察者、信道、任务、协议与实现版本的评测报告。

        进一步查阅 [Research Catalog](./catalog.md) 了解资源的任务、模态和核验状态；指标实现的证据等级见 [`camo-eval/VALIDATION.md`](https://github.com/MichaelCSHN/CamoGED/blob/main/camo-eval/VALIDATION.md)。

        ## 真实模型接入门槛

        Demo **不自动接入**新发现或新收录的模型。未来任何真实模型演示至少需要：

        1. Catalog 中存在规范记录，但“被收录”本身不代表已复现；
        2. 代码与权重来源、固定版本、许可证和模型卡可追溯；
        3. 输入输出契约、运行环境、推理命令和预测样例可复核；
        4. 数据上传、第三方服务和日志保留策略明确；
        5. 安全、隐私、两用风险和结果误读经过独立审查。
        '''
    ).strip()
    write("web/demo.md", demo)

    readme_path = "README.md"
    readme = read(readme_path)
    readme = readme.replace(
        "| Paper/dataset registry | metadata preview | coverage is selective; licenses may be unknown |",
        "| Awesome Camouflage | human-curated reading map | selection is editorial, not exhaustive or a reproduction claim |\n| Research Catalog | accepted metadata registry | automated discovery, human acceptance; records are metadata-only unless upgraded |",
    )
    link_note = (
        "\nThe curated [Awesome Camouflage](awesome/README.md) and the complete "
        "[Research Catalog](web/catalog.md) are separate products. Automated scans create candidates; "
        "only human-reviewed pull requests can accept or promote records.\n"
    )
    anchor = "Security reports use [`SECURITY.md`](SECURITY.md)."
    if link_note.strip() not in readme:
        readme = readme.replace(anchor, link_note + "\n" + anchor, 1)
    write(readme_path, readme)


def update_web_generation() -> None:
    path = "scripts/build_awesome.py"
    text = read(path)
    if "import json" not in text:
        text = text.replace("from __future__ import annotations\n\n", "from __future__ import annotations\n\nimport json\n")
    if 'WEB_PUBLIC = WEB / "public"' not in text:
        text = text.replace('WEB = ROOT / "web"\n', 'WEB = ROOT / "web"\nWEB_PUBLIC = WEB / "public"\n')

    catalog_functions = dedent(
        r'''
        def catalog_payload(resources: list[dict], config: dict) -> dict[str, object]:
            fields = (
                "id",
                "title",
                "venue",
                "year",
                "description",
                "resource_type",
                "pillars",
                "tasks",
                "modalities",
                "supervision",
                "method_families",
                "contexts",
                "publication_status",
                "verification_status",
                "curated",
                "curation_tier",
                "paper",
                "code",
                "last_verified",
            )
            output = []
            for item in sort_resources(resources):
                record = {field: item.get(field) for field in fields}
                record["authors"] = authors(item.get("authors", ""))
                output.append(record)
            return {
                "schema_version": "1.0",
                "coverage_through": config.get("coverage_through"),
                "last_human_review": config.get("last_human_review"),
                "resource_count": len(output),
                "resources": output,
            }


        def render_catalog(resources: list[dict], config: dict) -> str:
            type_counts = Counter(item.get("resource_type", "paper") for item in resources)
            task_counts = Counter(
                task for item in resources for task in as_list(item.get("tasks"))
            )
            modality_counts = Counter(
                modality for item in resources for modality in as_list(item.get("modalities"))
            )
            context_counts = Counter(
                context for item in resources for context in as_list(item.get("contexts"))
            )

            lines = [
                "---",
                "layout: page",
                "---",
                "",
                "# CamoGED Research Catalog",
                "",
                "> Complete accepted metadata catalog. Inclusion does not imply endorsement, full-text availability,",
                "> reproduced results, or a verified license. Use the status fields.",
                "",
                f"- Accepted records: **{len(resources)}**",
                f"- Coverage reviewed through: **{config.get('coverage_through', 'unknown')}**",
                f"- Verified metadata: **{sum(item.get('verification_status') == 'verified' for item in resources)}**",
                f"- Metadata-only: **{sum(item.get('verification_status') == 'metadata-only' for item in resources)}**",
                "",
                "## Coverage matrix",
                "",
                f"- Resource types: {', '.join(f'`{key}` {value}' for key, value in type_counts.most_common())}",
                f"- Leading tasks: {', '.join(f'`{key}` {value}' for key, value in task_counts.most_common(15))}",
                f"- Modalities: {', '.join(f'`{key}` {value}' for key, value in modality_counts.most_common())}",
                f"- Contexts: {', '.join(f'`{key}` {value}' for key, value in context_counts.most_common())}",
                "",
                "<CatalogExplorer />",
                "",
                "<details>",
                "<summary>Static fallback table</summary>",
                "",
                "| Year | Resource | Type | Tasks | Modalities | Supervision | Status | Links |",
                "|---:|---|---|---|---|---|---|---|",
            ]
            for item in sort_resources(resources):
                links = " ".join(
                    value
                    for value in [
                        link("source", item.get("paper")),
                        link("code", item.get("code")),
                    ]
                    if value
                )
                lines.append(
                    f"| {item.get('year') or ''} | **{md_escape(item['title'])}**<br>{md_escape(item.get('description') or '')} | "
                    f"`{md_escape(item.get('resource_type', 'paper'))}` | "
                    f"{md_escape(', '.join(as_list(item.get('tasks'))))} | "
                    f"{md_escape(', '.join(as_list(item.get('modalities'))))} | "
                    f"{md_escape(', '.join(as_list(item.get('supervision'))))} | "
                    f"{badge(item)}<br>reviewed {item.get('last_verified') or ''} | {links} |"
                )
            lines.extend(["", "</details>", ""])
            return "\n".join(lines)
        '''
    ).strip()
    text = replace_between(text, "def render_catalog", "def render_updates", catalog_functions)

    update_function = dedent(
        r'''
        def render_updates(config: dict, resources: list[dict]) -> str:
            latest = latest_resources(resources, 20)
            lines = [
                "---",
                "layout: page",
                "---",
                "",
                "# Awesome update status",
                "",
                f"- Coverage reviewed through: **{config.get('coverage_through', 'unknown')}**",
                f"- Last human review: **{config.get('last_human_review', 'unknown')}**",
                "- Automated candidates are not accepted records until a human-reviewed PR is merged.",
                "",
                "<AwesomeScanStatus />",
                "",
                "## Latest accepted records",
                "",
            ]
            lines.extend(resource_bullet(item) for item in latest)
            lines.extend(
                [
                    "",
                    "## Maintenance surfaces",
                    "",
                    "- Discovery query configuration: `data/discovery_queries.yaml`",
                    "- Candidate scanner: `scripts/discover_awesome.py`",
                    "- Candidate acceptance tool: `scripts/accept_awesome_candidates.py`",
                    "- Governance: `docs/AWESOME_GOVERNANCE.md`",
                    "",
                ]
            )
            return "\n".join(lines)
        '''
    ).strip()
    text = replace_between(text, "def render_updates", "def render_papers_page", update_function)

    old_write = 'def write(path: Path, content: str) -> None:\n    path.write_text(content.rstrip() + "\\n", encoding="utf-8")'
    new_write = dedent(
        r'''
        def write(path: Path, content: str) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")


        def write_json(path: Path, payload: dict[str, object]) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        '''
    ).strip()
    if old_write not in text:
        raise SystemExit("build_awesome write function marker not found")
    text = text.replace(old_write, new_write, 1)
    main_marker = '    write(WEB / "catalog.md", render_catalog(resources, config))\n    write(WEB / "updates.md", render_updates(config, resources))'
    main_replacement = (
        '    write(WEB / "catalog.md", render_catalog(resources, config))\n'
        '    write_json(WEB_PUBLIC / "catalog.json", catalog_payload(resources, config))\n'
        '    write(WEB / "updates.md", render_updates(config, resources))'
    )
    if main_marker not in text:
        raise SystemExit("build_awesome main marker not found")
    text = text.replace(main_marker, main_replacement, 1)
    write(path, text)

    theme = dedent(
        r'''
        import DefaultTheme from "vitepress/theme";
        import AwesomeScanStatus from "./components/AwesomeScanStatus.vue";
        import CamoDemo from "./components/CamoDemo.vue";
        import CatalogExplorer from "./components/CatalogExplorer.vue";
        import "./custom.css";

        export default {
          extends: DefaultTheme,
          enhanceApp({ app }) {
            app.component("AwesomeScanStatus", AwesomeScanStatus);
            app.component("CamoDemo", CamoDemo);
            app.component("CatalogExplorer", CatalogExplorer);
          }
        };
        '''
    ).strip()
    write("web/.vitepress/theme/index.js", theme)

    workflow_path = ".github/workflows/contracts.yml"
    workflow = read(workflow_path)
    awesome_step = "          python scripts/discover_awesome.py --self-test\n          python scripts/check_awesome.py"
    if "python scripts/check_cross_component.py" not in workflow:
        workflow = workflow.replace(
            awesome_step,
            awesome_step + "\n          python scripts/check_cross_component.py",
            1,
        )
    workflow = workflow.replace(
        "web/papers.md web/datasets.md web/leaderboard.md web/models.md",
        "web/papers.md web/datasets.md web/leaderboard.md web/models.md web/public/catalog.json",
    )
    write(workflow_path, workflow)


def close_backlog() -> None:
    backlog = dedent(
        r'''
        # Awesome cross-component follow-ups — closure record

        **Status: CLOSED — 2026-07-13**

        This record documents the items discovered during the Awesome specialist audit and the concrete implementation that closed each item. Future literature changes are handled through the normal fact-check and release process rather than reopening the original backlog implicitly.

        ## Book

        | Item | Resolution | Evidence |
        |---|---|---|
        | Explain curated Awesome vs complete Catalog | Appendix A now defines three layers: curated map, accepted metadata Catalog, and book citations | `book/chapters/appendix-resources.qmd` |
        | Expand Chapter 10 task map | Rebuilt as task/supervision/modality axes, including bbox RCOD, tracking, incomplete supervision, zero-shot/open-vocabulary, VLM and robustness | `book/chapters/10-intelligent-overview-datasets.qmd` |
        | Review 2025–2026 foundation-model literature | Added source-checked CamSAM2, MMCSBench and SDDF discussion, while keeping dynamic candidates outside the book | `book/chapters/14-foundation-models.qmd` |
        | Prevent Catalog-to-bibliography auto-copy | Appendix and search methodology explicitly require editorial adoption and primary-source review | `docs/BOOK_SEARCH_METHODOLOGY.md` |
        | Periodically reassess “first/largest/latest” | Added F15 and release-time dynamic-catalog review requirement | `docs/BOOK_FACTCHECK_REGISTER.md` |
        | Remove unsupported cross-domain foundation-model claim | Recast as a testable hypothesis with zero/few/full-supervision comparison requirements | F18 and Chapter 14.7 |

        ## Demo

        | Item | Resolution | Evidence |
        |---|---|---|
        | Keep Demo synthetic and local | Page states local browser handling and no model-inference claim | `web/demo.md`, `CamoDemo.vue` |
        | Link Catalog and metric validation | Added direct links and research-reporting boundary | `web/demo.md` |
        | Define real-model integration gate | Added code/weight provenance, version, license, input/output, privacy and safety requirements | `web/demo.md` |

        ## Website

        | Item | Resolution | Evidence |
        |---|---|---|
        | Multi-axis Catalog filtering | Generated JSON + client-side accessible filters with static fallback | `web/public/catalog.json`, `CatalogExplorer.vue` |
        | Public latest automated scan status | Read-only client widget fetches the latest public `awesome:triage` issue with session cache and failure fallback | `AwesomeScanStatus.vue`, `/updates` |
        | Explain Awesome/Catalog split at project root | Root component-status table and policy note updated | `README.md` |

        ## Enforcement

        `scripts/check_cross_component.py` and the Contracts workflow now block regressions in the book taxonomy, references, Demo boundary, interactive Catalog data, scan widget, README distinction and closure status.
        '''
    ).strip()
    write("docs/AWESOME_CROSS_COMPONENT_BACKLOG.md", backlog)


def main() -> None:
    update_book()
    update_factcheck_and_methodology()
    update_demo_and_readme()
    update_web_generation()
    close_backlog()
    print("Cross-component backlog remediation applied.")


if __name__ == "__main__":
    main()
