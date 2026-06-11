# Camouflage — 伪装的生成·识别·评价：开源全景计划

> **一句话定位**：把伪装当作一场跨越生物、军事、艺术与人工智能的"隐藏 ⇄ 揭示"协同演化博弈，建成全球唯一同时覆盖**生成、识别、评价**全链路、贯通**物理域 / 数字域 / 智能域**、整合**自然科学 / 军事 / 人文艺术**三视角的开源研究平台。
>
> 指导思想：人无我有、人有我新；知识与框架基于综述编撰，方法与实现提供 SOTA 全景，以 `coder / flowcamo / dualvcod` 三个原创项目为技术锚点。

---

## 〇、执行摘要（Executive Summary）

本计划构建一个"四位一体"的开源平台 **Camouflage**（候选缩写见 §1.3）：

- **一本专著**（在线先行、后出版）——系统梳理伪装的前世今生与理论-方法-技术-应用；
- **一个 Awesome 列表**——跨域资源精选，比现有列表更宽、更深、更活；
- **一个聚合网站**——论文库、模型库、动态 SOTA 排行榜、在线 Demo、数据集导航；
- **一套评测工具包** `camo-eval`——统一生成质量、检测精度、对抗鲁棒性三类评价标准。

与现有最强的同类资源（visionxiang / ChunmingHe 的 Awesome 列表、2024 CAAI《A Survey of COD and Beyond》）相比，本项目的**增量价值**在于：① 跨四大学科领域；② 同时覆盖生成+识别+评价（现有皆只做识别）；③ 提供"活的"平台（排行榜+Demo+工具包），而非静态综述；④ 以一条"协同演化博弈"主线贯穿全局（§1.4）。

---

## 一、项目定位与差异化分析

### 1.1 现有生态盘点

| 现有资源 | 覆盖范围 | 维护形态 | 关键不足 |
|----------|----------|----------|----------|
| awesome-camouflaged-object-detection (visionxiang) | 图像/视频 COD | 静态列表 | 仅检测；无生成、无评价工具、无跨域、无专著 |
| awesome-concealed-object-segmentation (ChunmingHe) | 隐藏目标分割 | 静态列表 | 同上，偏分割任务 |
| Awesome-Camouflaged-Object-Detection (clelouch) | 深度学习 COD | 静态列表 | 同上 |
| 《A Survey of COD and Beyond》(CAAI AIR, 2024) | 传统+深度 COD、扩展任务 | 论文（一次性） | 系统但静态；不含生成与对抗；无可运行资源 |
| 生物学/军事伪装专著 | 单一领域 | 图书 | 不含计算技术域 |

> **致谢与区隔**：本项目明确以上述 Awesome 列表与 2024 综述为出发点，并在 Awesome 与专著中显式致谢、互链。我们不重复其检测部分的逐条罗列，而是**补齐生成、评价、跨域、活资源**四块空白，并以统一主线重新组织。

### 1.2 差异化价值

```
人无我有
  ✦ 唯一跨「自然科学 / 军事 / 人文艺术 / 计算机视觉」四领域的伪装综合平台
  ✦ 唯一同时覆盖「生成 + 识别 + 评价」全链路的开源专著
  ✦ 唯一系统刻画「物理域 → 数字域 → 智能域」演进脉络的资源
  ✦ 唯一配套「生成质量 + 检测精度 + 对抗鲁棒性」三类评价工具包

人有我新
  ✦ 比现有 Awesome 更宽（跨域）、更深（含原创方法）、更活（自动化动态更新）
  ✦ 以「协同演化博弈」为学术主线，把四领域真正缝合而非并列拼盘
  ✦ 以 coder / flowcamo / dualvcod 三项目提供可复现、可对比、可在线推理的实证锚点
```

### 1.3 命名与品牌

主名 **Camouflage**。候选缩写/副标识（择一作为组织名与域名）：

- **CamoVerse**（伪装宇宙，强调全景与跨域，推荐）
- **OpenCamo**（强调开源属性）
- **CamoHub**（强调资源聚合）

建议：GitHub 组织名 `CamoVerse`，主域名 `camoverse.org` 或 `camoverse.github.io`，专著定名 **《Camouflage: Generation, Recognition, and Evaluation Across Nature, War, and Machines》**（中文：《伪装：生成、识别与评价——自然、战争与机器的跨域综观》）。

### 1.4 学术主线（本项目的智识内核）★

把四个看似不相关的领域真正缝合的，是一条统一命题：

> **伪装是"隐藏方"与"揭示方"之间的协同演化博弈（co-evolutionary arms race）。**

这条主线在四个领域里是同一个数学/动力学结构的不同实例：

| 领域 | 隐藏方 | 揭示方 | 博弈机制 |
|------|--------|--------|----------|
| 自然 | 猎物的拟态/隐蔽 | 捕食者的视觉搜索 | 自然选择驱动的军备竞赛 |
| 军事 | 迷彩/假目标/隐身 | 侦察/探测/识别 | 措施—反措施循环 |
| 艺术 | 错视/隐藏图形 | 观看者的知觉 | 注意与预期的操纵 |
| AI | 生成器 / 对抗攻击 | 判别器 / 检测器 / 防御 | GAN、对抗攻防、检测-反检测 |

**意义**：这一框架使"生成"（隐藏方）与"识别"（揭示方）成为同一枚硬币的两面，"评价"则是裁判这场博弈胜负的标尺。它为全书提供叙事骨架，也是区别于一切现有综述的原创学术贡献，可单独发表为一篇观点/综述论文。

---

## 二、整体架构：四位一体平台

```
CamoVerse/  (GitHub Organization)
│
├── 📚 camouflage-book/      专著源码（Quarto；HTML + PDF + ePub 多格式）
│
├── 🌟 awesome-camouflage/   跨域 Awesome 精选列表
│
├── 🌐 camouflage-web/       聚合网站（VitePress / Docusaurus）
│      ├─ /papers            论文库（可检索）
│      ├─ /models            模型库（Model Zoo + 权重）
│      ├─ /leaderboard       动态 SOTA 排行榜
│      ├─ /demo              在线交互 Demo
│      └─ /datasets          数据集导航
│
├── 🔧 camo-eval/            评测工具包（生成/检测/鲁棒性三类指标）
│
└── 🔬 coder / flowcamo / dualvcod   三个原创项目（接入）
```

**仓库职责划分**

| 仓库 | 职责 | 主语言/工具 | 许可证 |
|------|------|-------------|--------|
| `camouflage-book` | 专著（含可执行代码） | Quarto (md+ipynb) | 内容 CC-BY-4.0 / 代码 Apache-2.0 |
| `awesome-camouflage` | 精选资源列表 | Markdown | CC0 / CC-BY-4.0 |
| `camouflage-web` | 聚合网站 | VitePress + JS | MIT |
| `camo-eval` | 评测工具包 | Python | Apache-2.0 |
| `coder/flowcamo/dualvcod` | 原创方法 | Python/PyTorch | Apache-2.0（按需） |

---

## 三、专著结构：《伪装：生成·识别·评价》

### 3.1 定位与工具链

- **语言**：中英双语（独立分支或并排切换；优先英文以扩大影响，中文同步）。
- **载体**：**Quarto** 主选——理由：原生支持可执行代码（Python/R/Julia/JS）、文献引用与交叉引用、公式编号、callout，并一键渲染 HTML/PDF/ePub/Word，适合"在线先行 + 后出版"。备选 Jupyter Book（生态相近）与 mdBook（更轻但缺学术特性）。
- **体例**：每章 = 综述脉络 + 方法详解 + 可运行代码示例 + 数据集/指标表 + 内嵌或外链 Demo。
- **可复现**：关键图表由代码现场生成；提供 `binder` / `colab` 一键运行入口。

### 3.2 三种组织视角的统一（解决"任务 vs 域"张力）

全书按**任务三支柱**（生成 / 识别 / 评价）为主轴分篇，每篇内部再按**物理 / 数字 / 智能**三域展开，并始终以 §1.4 的博弈主线串联。读者既可纵读（按任务）也可横查（按域）。下表为全书的"任务 × 域"导航矩阵：

| | 物理域 | 数字域 | 智能域 |
|---|---|---|---|
| **生成** | 迷彩材料/图案、物理对抗迷彩 (Ch5–6) | 隐写、Deepfake、数字对抗 (Ch8–9) | GAN/扩散生成、flowcamo (Ch11) |
| **识别** | 多光谱/红外/偏振探测 (Ch7) | 篡改检测、对抗样本检测 (Ch9) | 图像/视频/实例 COD、coder/dualvcod (Ch12–14) |
| **评价** | 物理可实现性、隐蔽性度量 (Ch6/15) | 检测可靠性 (Ch9/15) | Sm/Fw/Em/MAE、生成质量、鲁棒性 (Ch15) |

### 3.3 章节大纲

#### 第一篇　伪装的前世今生（跨域综述 · 隐藏与揭示的博弈）

**第1章　伪装的本质与统一框架**
- 1.1 哲学与认知定义：concealment / masquerade / mimicry / deception
- 1.2 分类学：主动 vs 被动；空间/信号/认知层；隐藏方 vs 揭示方
- 1.3 跨域统一框架：物理域 · 数字域 · 智能域
- 1.4 **核心主线：协同演化博弈**（贯穿全书的理论骨架）
- 1.5 本书体例、矩阵导航与阅读路径

**第2章　自然界的伪装——生物学视角**
- 2.1 生物学基础：crypsis / disruptive coloration / countershading / masquerade / mimicry
- 2.2 颜色伪装机制：变色龙、头足类、昆虫
- 2.3 纹理与形态：叶尾壁虎、竹节虫、枯叶蝶
- 2.4 运动与伪装：运动暴露 vs 运动眩惑（MoCA 数据集的生物原型）
- 2.5 捕食者视觉搜索：注意、搜索图像、破伪机制
- 2.6 生物伪装对 AI 算法的启示（边界破坏 → 检测器的边界线索）

**第3章　军事伪装——战略欺骗的艺术与科学**
- 3.1 简史：18 世纪散兵绿 → WWI 法军伪装 → 数字迷彩
- 3.2 迷彩图案谱系：WWII → 冷战 → 现代多光谱/像素迷彩
- 3.3 多频段隐身：可见光 / 红外 / 雷达 / 太赫兹协同
- 3.4 军事欺骗（MILDEC）与假目标战术
- 3.5 当代智能伪装材料：相变、电致变色、自适应变色
- 3.6 军事目标检测与数据集：MilDetr、MHCD2022
- 3.7 文化演化视角：迷彩作为政治认同（Royal Society B 研究）

**第4章　伪装在艺术与文化中**
- 4.1 错视艺术（trompe l'œil）与隐藏图形史
- 4.2 迷彩作为美学符号：立体主义 dazzle、Warhol 迷彩系列
- 4.3 隐形叙事与文化想象
- 4.4 数字时代的伪装美学与生成艺术

#### 第二篇　生成篇：如何制造"隐藏"

**第5章　物理域伪装生成**
- 5.1 迷彩图案设计原理：颜色匹配、纹理频率、边界破坏、对比度
- 5.2 多频段伪装材料：雷达吸波、红外低发射、太赫兹
- 5.3 主动伪装系统：自适应变色、电子皮肤
- 5.4 3D 打印与定制化制造

**第6章　物理对抗伪装（Physical Adversarial Camouflage）**
- 6.1 对抗基础：FGSM → PGD → 物理约束（EOT、可微渲染）
- 6.2 贴片攻击 vs 全覆盖迷彩纹理攻击
- 6.3 代表方法谱系：DAS → FCA → DTA → ACTIVE → RAUCA → PhyCamo
- 6.4 3D 几何感知：可微渲染 / NeRF / 3D Gaussian Splatting 驱动
- 6.5 单视图重建：CAM3D（Mamba 增强跨域 3D 对抗伪装）
- 6.6 评价：AP@0.5、多视角鲁棒性、物理可实现性、人眼隐蔽性
- 6.7 与遥感/航拍场景的结合

**第7章　数字域伪装生成**
- 7.1 信息隐藏与隐写（含深度隐写）
- 7.2 Deepfake 作为身份伪装
- 7.3 数字对抗：无限制对抗样本、语义化隐蔽攻击（AdvCam / 风格迁移）
- 7.4 基于扩散模型的对抗样本生成
- 7.5 自然对抗样本（NaturalAE）与内容篡改

**第8章　智能域伪装生成（AIGC × 伪装）**
- 8.1 经典：纹理合成、Poisson 融合、背景一致性
- 8.2 GAN 路线：CycleGAN 风格迁移、条件生成
- 8.3 扩散路线：CamDiff、SCODE（合成数据增强 COD）
- 8.4 神经风格迁移的隐蔽对抗纹理
- 8.5 **[原创] flowcamo 的视频伪装生成分支**
- 8.6 生成-检测闭环：用生成数据反哺检测训练（呼应 §1.4 博弈主线）

#### 第三篇　识别篇：如何揭示"隐藏"

**第9章　物理域与数字域的伪装识别**
- 9.1 可见光目标检测（YOLO 系列、MilDetr）
- 9.2 红外/热成像探测
- 9.3 多光谱融合（MCOD 数据集）
- 9.4 偏振光辅助检测（含 polarization-guided COD）
- 9.5 遥感场景伪装目标检测
- 9.6 数字域：篡改检测、对抗样本检测与防御

**第10章　智能域伪装识别总览与数据集**（见 §3.4 数据集表）
- 10.1 任务定义、挑战与评价口径
- 10.2 数据集全景（图像 / 视频 / 多光谱 / 多模态）
- 10.3 训练协议与跨数据集泛化约定

**第11章　图像伪装目标检测（Image COD）**
- 11.1 传统方法：频率分析、显著性对比、手工特征
- 11.2 CNN 时代：SINet/SINetV2、PFNet、SegMaR、ZoomNet
- 11.3 Transformer 时代：FSPNet、ZoomNeXt、HGINet、SPEGNet
- 11.4 频域方法：Frequency-Spatial Entanglement、频率引导适配
- 11.5 图神经网络与胶囊路由（Mamba Capsule）
- 11.6 弱监督 / 半监督 / 噪声标签（ST-SAM、scribble、point）
- 11.7 **[原创] coder 方法详解**（动机、架构、消融、SOTA 对比）

**第12章　视频伪装目标检测（Video COD）**
- 12.1 特殊挑战：时序一致性、运动线索、相机运动
- 12.2 光流引导：SAM-PM、ZS-VCOS
- 12.3 记忆与时空建模：检索记忆、episodic memory
- 12.4 SAM2 时代：CamSAM2、CamoSAM2、SAM2 适配评测
- 12.5 **[原创] flowcamo：运动感知视频伪装检测**（与生成分支的统一）

**第13章　实例级与扩展任务**
- 13.1 伪装实例分割（CIS）vs 语义分割
- 13.2 计数与排序（ranking）
- 13.3 **[原创] dualvcod：双路径视频伪装实例检测**
- 13.4 指代伪装检测（Referring COD，R2C7K）
- 13.5 协同伪装检测（Collaborative COD，CoCOD8K）
- 13.6 开放词汇伪装分割（OVCOS）

**第14章　基础模型时代的伪装识别**
- 14.1 SAM/SAM2 在隐藏场景的局限与适配（SAM-Adapter、双流适配器）
- 14.2 CLIP 零样本伪装检测
- 14.3 DINOv2/DINOv3 特征表示
- 14.4 多模态大语言模型（MLLM）× 伪装（MM-CamObj）
- 14.5 通用显著/伪装双任务（VSCode）、提示学习
- 14.6 跨界应用：医学（息肉/病灶）、工业缺陷、农业（PlantCamo、ACOD-12K）

#### 第四篇　评价篇：如何裁判这场博弈（本书与标题对齐的重点）★

**第15章　伪装评价的统一标尺**
- 15.1 **识别质量评价**
  - 像素级：MAE、加权 F-measure ($F_\beta^w$)
  - 结构级：S-measure ($S_\alpha$)
  - 对齐级：增强 E-measure ($E_\phi$)
  - 实例级：AP / AR；视频级：时序一致性、$\mathcal{J}\&\mathcal{F}$
- 15.2 **生成质量评价**
  - 视觉真实性：FID、LPIPS、用户研究
  - 伪装有效性：对检测器的成功欺骗率、可检测度下降
  - 隐蔽性 vs 攻击性的权衡曲线
- 15.3 **对抗鲁棒性评价**
  - 攻击成功率、AP@0.5 下降、跨模型迁移性
  - 物理可实现性、多视角/多光照鲁棒性
- 15.4 **跨域与人因评价**
  - 人类知觉搜索实验范式（反应时、命中率）
  - 与生物学/军事评价口径的对照
- 15.5 评价的陷阱：数据泄漏、指标博弈、不可比的训练协议
- 15.6 `camo-eval` 工具包：统一复现与论文表格自动生成

**第16章　前沿、挑战与展望**
- 16.1 当前主要挑战（提炼自 2024 综述并延伸至生成与评价）
- 16.2 3D / 4D 场景伪装理解（NeRF、3DGS、动态场景）
- 16.3 具身智能中的主动伪装感知
- 16.4 生成-识别协同演化的统一博弈论框架（呼应 §1.4，可作为开放研究纲领）
- 16.5 两用性、安全与伦理（与 §九 呼应）

### 3.4 数据集全景表（专著与网站共用）

> 规模数字以官方论文为准；"—"表示需在编撰时核实填写。建议每条附下载链接、许可证与 BibTeX。

| 数据集 | 任务/模态 | 规模 | 划分/用途 | 备注 |
|--------|-----------|------|-----------|------|
| CHAMELEON | 图像 COD | 76 | 仅测试 | 早期小规模，常因偏差弃用 |
| CAMO | 图像 COD | 1,250（含1,250非伪装） | 1,000 训 / 250 测 | 首个完整标注 |
| COD10K | 图像 COD | 5,066 伪装（共约10K） | 3,040 训 / 2,026 测，78 子类 | 当前最大图像基准 |
| NC4K | 图像 COD | 4,121 | 仅测试（泛化） | 含排序标注 |
| CoCOD8K | 协同 COD | 8K | 训/测 | 协同伪装 |
| R2C7K | 指代 COD | 7K | 训/测 | Referring |
| PlantCamo | 植物伪装 | — | 训/测 | 植物场景 |
| ACOD-12K | 农业伪装 | 12K | 训/测 | 密集农业场景 |
| MHCD2022 | 军事伪装 | 3,000 | 5 类 | 军事高阶 |
| MCOD | 多光谱 COD | — | 基准 | 首个多光谱基准 |
| MM-CamObj | 多模态 | — | 问答/检测 | MLLM 评测 |
| MoCA-Mask | 视频 COD | 141 视频序列 | 训/测 | 移动伪装动物 |
| CAD | 视频 COD | — | 测试 | 早期视频 |
| CamoVid60K | 视频 COD | 60K 帧 | 训/测 | 大规模视频 |
| MSVCOD | 视频 COD（多场景） | — | 训/测 | 多场景 |

---

## 四、Awesome Camouflage 精选列表

### 4.1 结构（按"博弈主线 + 任务三支柱"组织，差异化）

```
# Awesome Camouflage 🦎  — Generation · Recognition · Evaluation across Nature, War & Machines

## 📖 Books, Monographs & Theses        ← 现有列表均无此分类
## 🧭 Surveys & Foundational Papers       （含致谢现有综述与 Awesome 列表）

## 🌿 Natural Camouflage
   - Biology reviews (Cott 1940, Ruxton et al. 2018 …)
   - Mechanisms (disruptive coloration, countershading, mimicry)
   - Animal coloration datasets
## 🪖 Military Camouflage
   - Historical archives & pattern databases
   - Multispectral / IR / radar stealth
   - Military deception (MILDEC)
## 🎨 Camouflage in Art & Culture
   - Trompe l'œil, dazzle, fashion

## ✍️ Generation  (隐藏方)
   - Physical adversarial camouflage (DAS/FCA/DTA/ACTIVE/RAUCA/PhyCamo/CAM3D)
   - Digital adversarial & steganography & deepfake
   - Generative models for camouflage (CamDiff/SCODE/style-transfer)
## 🔎 Recognition  (揭示方)
   - Datasets (tabulated: type / size / modality / link / cite)
   - Image COD (by year × venue)
   - Video COD
   - Instance segmentation / counting / ranking
   - Extended tasks (referring / collaborative / open-vocab)
   - Foundation-model adaptations (SAM/SAM2/CLIP/DINO/MLLM)
   - Multispectral / IR / polarization / remote sensing
## 📊 Evaluation  (裁判)
   - Metrics & toolkits (Sm/Fw/Em/MAE, FID/LPIPS, robustness)
   - Benchmarks & public leaderboards
   - Human-perception studies

## 🔬 Our Research Projects
   - coder  /  flowcamo  /  dualvcod
## 🌐 Demos, Tools & Tutorials
## 🏛️ Workshops, Challenges & Venues
## 🤝 Acknowledgements & Related Lists   （显式致谢 visionxiang / ChunmingHe / clelouch）
```

### 4.2 差异化设计点

- 论文条目统一五字段：**venue / year / code / dataset / metric**（可直接被网站脚本解析）。
- 数据集条目五字段：**类型 / 规模 / 模态 / 下载 / 引用数**。
- 每个大类附"推荐入门路径"（3–5 篇必读）。
- 顶部 badge：最后更新日期、收录条目数、awesome.re 徽章。
- **机器可读**：列表用结构化注释（或并存 `data/*.yaml`），网站直接消费，避免双重维护。

---

## 五、聚合网站设计

### 5.1 技术栈

- **框架**：VitePress（轻量、Markdown 友好、静态部署）；若需更丰富插件生态可选 Docusaurus。
- **部署**：GitHub Pages（主）+ Vercel（镜像）。
- **搜索**：Algolia DocSearch（开源项目可免费申请）。
- **图表**：ECharts / Plotly（交互式性能曲线）。
- **数据源**：单一事实来源 = `awesome-camouflage/data/*.yaml`，网站与 Awesome 共享，CI 校验一致性。

### 5.2 核心页面

**/leaderboard — 动态 SOTA 排行榜**

```
┌──────────────────────────────────────────────────────────────┐
│  COD Leaderboard   [Dataset ▼ COD10K] [Task ▼ Image] [Year ▼]  │
├──────┬───────────────┬───────┬───────┬───────┬───────┬────────┤
│ Rank │ Method        │  Sm↑  │  Fw↑  │  Em↑  │  M↓   │ Params │
├──────┼───────────────┼───────┼───────┼───────┼───────┼────────┤
│  1   │ (示例占位)     │  —    │  —    │  —    │  —    │  —     │
│  2   │ coder (ours)  │  —    │  —    │  —    │  —    │  —     │
└──────┴───────────────┴───────┴───────┴───────┴───────┴────────┘
   ⚠ 所有数值在编撰时从原论文/复现核实填入；上线前不展示占位数字。
```

- 数据来自 `data/leaderboard.yaml`，每行附出处链接（arXiv/官方仓库）与是否官方/复现标记。
- 支持按 数据集 / 任务 / 年份 / 参数量 筛选与排序。
- **可信度优先**：每个数字标注来源与协议；区分"原论文报告"与"本平台复现"。

**/demo — 在线推理**
- Image COD（coder 及对照方法）、Video COD（flowcamo）、Instance（dualvcod）。
- "多模型并排对比"：上传一张图，多模型同屏输出 + 误差热力图。
- 后端：HuggingFace Spaces（Gradio），配额受限时降级为离线样例画廊。

**/datasets — 数据集导航**：卡片 + 样例图 + 模态/任务/规模筛选 + 下载 + BibTeX。

**/papers — 论文库**：按年份/会议/任务检索，链接 arXiv/Semantic Scholar 摘要。

**/models — 模型库**：权重、配置、复现命令、`camo-eval` 一键评测脚本。

---

## 六、技术工具包：camo-eval

### 6.1 设计目标

统一三类评价：**识别精度、生成质量、对抗鲁棒性**；目标是成为领域"事实标准"评测库（类比 PySODMetrics 但更全），从而反向带动平台影响力。

### 6.2 接口示例

```python
from camo_eval import CODEvaluator, GenEvaluator, RobustEvaluator

# 1) 识别精度
cod = CODEvaluator(pred_dir="preds/", gt_dir="gts/",
                   metrics=["Sm", "Fw", "Em", "MAE"])
res = cod.evaluate()
cod.plot_pr_curve(); cod.export_latex_table("table.tex")

# 2) 生成质量（伪装合成 / 对抗迷彩）
gen = GenEvaluator(real_dir="real/", fake_dir="fake/",
                   metrics=["FID", "LPIPS", "deception_rate"],
                   victim_detector="yolov8")

# 3) 对抗鲁棒性
rob = RobustEvaluator(model="coder", attacks=["pgd", "physical"],
                      report=["asr", "ap_drop", "transferability"])
```

### 6.3 模块结构

```
camo-eval/
├── metrics/
│   ├── detection/   smeasure.py  emeasure.py  fmeasure.py  mae.py  ap.py
│   ├── video/       j_and_f.py   temporal_consistency.py
│   ├── generation/  fid.py  lpips.py  deception_rate.py
│   └── robustness/  asr.py  ap_drop.py  transferability.py
├── datasets/        loaders.py  video_loader.py  registry.py
├── visualization/   pr_curve.py  comparison.py  error_map.py
└── export/          latex_table.py  leaderboard_push.py
```

---

## 七、三个原创项目的整合定位

| 项目 | 定位 | 专著位置 | 网站接入 | Awesome | camo-eval |
|------|------|----------|----------|---------|-----------|
| **coder** | 智能域图像 COD 原创核心 | 第11.7节详解 | /demo 图像、/leaderboard | Recognition→Image COD 置顶 | 注册为基准模型 |
| **flowcamo** | 运动感知视频伪装"生成+检测"双线 | 第8.5节（生成）+ 12.5节（检测） | /demo 视频 | Generation 与 Recognition 双列 | 视频指标基准 |
| **dualvcod** | 双路径视频伪装实例检测 | 第13.3节详解 | /demo 实例分割 | Recognition→Instance 置顶 | 实例指标基准 |

> 三项目共同体现 §1.4 主线：flowcamo 同时跨"生成（隐藏方）"与"检测（揭示方）"，是博弈闭环的最佳示范案例。

---

## 八、开源治理与可持续性

### 8.1 许可证策略
- 代码：Apache-2.0（含专利授权，比 MIT 更适合可能的产业使用）。
- 专著正文与 Awesome 内容：CC-BY-4.0（署名即可转载，利于传播与后续出版）。
- 数据：不再分发，仅提供链接并标注上游许可证，规避数据版权风险。

### 8.2 学术可引用
- `CITATION.cff` 提供标准引用元数据。
- 通过 **Zenodo** 为每个发布版本铸造 **DOI**，使专著/工具包可被正式引用。
- 专著各章可独立标注版本与 DOI。

### 8.3 贡献与社区
- `CONTRIBUTING.md` + PR 模板 + Issue 模板（新增论文/数据集/方法的标准化表单）。
- 行为准则（Contributor Covenant）。
- GitHub Discussions 作为社区入口（替代独立 Discord，降低维护成本）。
- 维护者轮值与 `CODEOWNERS`。

### 8.4 自动化（降低维护负担，对应"更活"）
- GitHub Actions：每周自动抓取 arXiv 新论文候选 → 生成待审 Issue。
- CI 校验：Awesome 链接有效性、`data/*.yaml` 与网站/排行榜一致性、专著可构建。
- 自动部署：合并即重建网站与专著。

### 8.5 版本与发布节奏
- 语义化版本（专著 `v0.x` 在线预览 → `v1.0` 出版同步）。
- 季度 release，附 changelog 与 Zenodo DOI。

---

## 九、两用性、安全与伦理（必读声明）★

本项目涵盖军事伪装与对抗攻击等**潜在两用（dual-use）**内容。为负责任地开源，约定：

- **教育与防御导向**：所有对抗/军事内容以理解机理、提升检测与防御鲁棒性为目的，配套呈现防御方法与评测。
- **不提供可直接武器化的产物**：不发布针对特定真实型号装备的攻击配方、可即用的物理迷彩制造参数等具操作性的危害细节；对抗示例聚焦公开学术基准与方法层面。
- **数据合规**：仅链接、不再分发受限数据；尊重上游许可证与隐私。
- **责任披露**：若涉及对真实部署系统的脆弱性，遵循 responsible-disclosure 流程。
- **伦理声明**显式置于专著（第16.5节）、README 与 Awesome 顶部。

---

## 十、成功指标（KPI）与里程碑

| 维度 | 6 个月目标 | 12 个月目标 |
|------|-----------|-------------|
| GitHub Stars（主仓+Awesome） | 500+ | 2,000+ |
| Awesome 收录条目 | 300+ | 600+ |
| 专著章节（在线） | 第一篇 + 评价篇 | 全四篇 v1.0 |
| Demo 任务数 | 图像 COD | 图像/视频/实例 |
| 外部贡献者 | 5+ | 20+ |
| 学术产出 | arXiv 主线观点论文投稿 | 综述/benchmark 论文 + 专著投稿 |
| 收录 | awesome.re 申请 | PapersWithCode 对接、被他人综述引用 |

---

## 十一、分阶段路线图（含资源假设）

> **资源假设**：核心 1–2 人 + 若干兼职贡献者。下列时间线为"全力投入"估计；若人力有限，按 §11.5 的 MVP 优先级裁剪。

### Phase 1 — 奠基（第 1–2 月）
- [ ] 建 GitHub Org（CamoVerse）+ 各仓库骨架 + 许可证 + CITATION.cff
- [ ] Awesome v0.5（≥150 条，含致谢与机器可读 yaml）
- [ ] 专著工具链（Quarto）跑通；完成第1章（含主线 §1.4）+ 评价篇大纲
- [ ] camo-eval 识别指标（Sm/Fw/Em/MAE）可用 + 单元测试
- [ ] 网站 skeleton 上线（VitePress + Pages）
- **产出**：README + Awesome v0.5 + 网站骨架 + camo-eval v0.1

### Phase 2 — 扩充（第 3–4 月）
- [ ] 专著第一篇 + 评价篇（第15章）完成
- [ ] coder 接入 /demo 与 /leaderboard；camo-eval 注册基准
- [ ] Leaderboard 上线（COD10K/CAMO/NC4K，数值核实填入）
- [ ] 数据集导航页完成；Awesome v1.0（≥300 条）
- **产出**：专著 v0.4 + Demo v1 + Leaderboard v1 + Awesome v1.0

### Phase 3 — 深化（第 5–6 月）
- [ ] 生成篇 + 识别篇完成；flowcamo/dualvcod 接入
- [ ] 视频 + 实例 Demo 上线；camo-eval 增加生成/鲁棒性指标
- [ ] Awesome 自动更新（Actions）；中英内容对齐
- [ ] arXiv 发布主线观点/综述论文 v1
- **产出**：专著 v0.8 + Demo v2 + camo-eval v0.5 + Awesome v2.0

### Phase 4 — 出版冲刺（第 7–12 月）
- [ ] 专著全文定稿、图表精修、双语校对
- [ ] 投稿出版社（见 §十二）+ 配套综述/benchmark 论文投稿
- [ ] 社区建设（Discussions、贡献者扩展）；Zenodo DOI；申请 awesome.re / PapersWithCode
- **产出**：专著 v1.0（在线）+ 出版投稿 + 稳定社区

### 11.5 MVP 优先级（若资源受限，按此顺序保底）
1. Awesome 列表 + 致谢（最低成本、最快见效）
2. camo-eval 识别指标（领域刚需，易获采用）
3. 专著"评价篇 + 主线章"（最具差异化的智识贡献）
4. coder 的 /demo + Leaderboard（实证锚点）
5. 其余生成/视频内容逐步补全

---

## 十二、专著出版路径

**先在线、后出版**三步走：

1. **在线版先行**（Quarto 渲染，CC-BY-4.0 + Zenodo DOI），积累引用与社区。
2. **配套论文铺垫**：先发 1 篇主线观点/综述（投 ACM Computing Surveys / TPAMI / IEEE TASE 等），建立学术信誉与引用。
3. **以影响力换邀稿**：凭引用量与社区规模接触出版社。

| 路径 | 候选 | 适配理由 |
|------|------|----------|
| 国际 | Springer（Synthesis Lectures / LNCS 专著线）、Cambridge UP、MIT Press、Now Publishers (FnT) | 跨学科与计算视觉定位皆可；Now 的 Foundations and Trends 系列尤其适合"综述型专著" |
| 国内 | 科学出版社、电子工业出版社、清华大学出版社 | 中文版与教材化路径 |

---

## 十三、风险登记与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 范围过大、烂尾 | 高 | 按 §11.5 MVP 优先级；季度可交付物 |
| 维护负担不可持续 | 高 | 自动化（§8.4）+ 社区贡献 + 单一数据源 |
| 数据/版权风险 | 中 | 只链接不分发；标注上游许可证 |
| 两用性争议 | 中 | §九 伦理声明 + 防御导向 + 不发可武器化细节 |
| 排行榜数字不可比/造假争议 | 中 | 标注来源与协议；区分原报告/复现 |
| 与现有综述重叠被质疑 | 中 | 显式致谢 + 聚焦生成/评价/跨域/活资源增量 |
| 三项目尚未成熟即曝光 | 中 | 先以 Demo + 基准形式接入，论文成熟后再重点宣传 |

---

## 十四、差异化卖点（总览图）

```
                       协同演化博弈（隐藏 ⇄ 揭示）   ← 贯穿主线
                                 │
        ┌────────────────────────┼────────────────────────┐
     自然科学                   军事                     人文艺术      ← 三视角
        └────────────────────────┼────────────────────────┘
                                 │
                  物理域 ── 数字域 ── 智能域                 ← 三技术域
                                 │
                ┌────────────────┼────────────────┐
              生成              识别              评价         ← 三支柱
            (隐藏方)          (揭示方)          (裁判)
                │                │                │
            flowcamo         coder            camo-eval
            (生成分支)      (图像COD)         (统一标尺)
                │           dualvcod              │
                └───────── (视频实例) ────────────┘
```

**独特价值**：让生物学家、军事研究者、艺术学者与 AI 工程师在同一平台各取所需；让计算机视觉研究者既看懂领域来龙去脉，又能一键复现、对比、评测——并以一条"协同演化博弈"主线把这一切缝合为一个有思想的整体，而非资源堆叠。

---

## 附录：关键参考与资源

**综述/主线参考**
- Xiao et al., *A Survey of Camouflaged Object Detection and Beyond*, CAAI AIR, 2024（检测综述基线）
- 军事/生物对照：*Cultural evolution of military camouflage*, Phil. Trans. R. Soc. B；*Military mimicry: concealment, deception, and imitation*, 2024

**SOTA 方法（2024–2025，编撰时核实指标）**
- ZoomNeXt (TPAMI 2024)、HGINet (TIP 2024)、SPEGNet、Mamba Capsule Routing
- 视频：SAM-PM、CamSAM2、CamoSAM2、SAM2 适配评测
- 生成/对抗：DAS/FCA/DTA/ACTIVE/RAUCA、PhyCamo (AAAI 2025)、CAM3D (2025)、CamDiff、SCODE
- 基础模型：SAM-Adapter、双流适配器 (ICCV 2025)、VSCode、KGDA

**核心数据集**：见 §3.4 表（COD10K / CAMO / NC4K / MoCA-Mask / CamoVid60K / MCOD / MM-CamObj 等）

**现有 Awesome（致谢与互链）**
- visionxiang/awesome-camouflaged-object-detection
- ChunmingHe/awesome-concealed-object-segmentation
- clelouch/Awesome-Camouflaged-Object-Detection
- GuoleiSun/Awesome-SAM2

**工具与平台**
- 专著：Quarto（主）/ Jupyter Book / mdBook（备）
- 网站：VitePress / Docusaurus；搜索 Algolia DocSearch
- Demo：HuggingFace Spaces (Gradio)
- 治理：CITATION.cff、Zenodo DOI、GitHub Actions、Contributor Covenant
