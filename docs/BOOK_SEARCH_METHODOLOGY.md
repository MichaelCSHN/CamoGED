# 文献检索与纳入方法

本文件用于支撑书稿中的“尚未发现同类专著”“首个数据集”“当前主要基准”等结论。它是可更新的检索记录，而不是一次性宣传材料。

## 检索范围

- 学术数据库：Web of Science、Scopus、Google Scholar、Crossref、Semantic Scholar；
- 图书与馆藏：WorldCat、主要大学出版社目录、国家图书馆目录；
- 标准与官方资料：NIST、NATO/STO、政府审计与军种公开资料；
- 计算机视觉：CVF Open Access、IEEE Xplore、ACM Digital Library、SpringerLink、arXiv；
- 项目与数据：论文官方项目页、作者仓库、数据集发布页。

## 核心检索组

1. camouflage / crypsis / masquerade / mimicry / concealment；
2. military camouflage / signature management / target acquisition；
3. camouflage art / dazzle / camoufleurs / visual perception；
4. camouflaged object detection / concealed object segmentation / video camouflage；
5. adversarial camouflage / physical adversarial attack；
6. camouflage evaluation / detectability / visual search / human factors。

每组分别与 book、handbook、survey、dataset、benchmark、evaluation、generation、detection 等组合检索。中文检索同步使用“伪装、隐蔽、拟态、迷彩、伪装目标检测、伪装评价”等词。

## 纳入与排除

纳入：正式专著、同行评审论文、标准、公开技术报告、可核验数据集和方法项目。预印本可以纳入前沿讨论，但必须标明状态。排除：无法追溯来源的媒体转述、只有营销演示而无方法说明的项目、重复发布版本、无法确认许可或身份的镜像资源。

## 结论用语

穷尽性结论统一写为：

> 据本书截至 YYYY-MM-DD 对上述数据库、关键词和语种范围的检索，尚未发现……

“首个、最大、当前”等结论必须在 `docs/BOOK_FACTCHECK_REGISTER.md` 中留下核验记录，并在版本发布前重新检索。



## 与动态 Catalog 的关系

Awesome 自动发现每周从 arXiv 与 Crossref 生成候选报告，但候选只能作为检索线索。自动流程不得直接修改书稿、事实核查状态或参考文献。编辑在准备新版本时应：

1. 检查自上次 `coverage_through` 之后的 triage issues；
2. 对影响“首个、最大、最新、主要基准”等表述的候选回查一手来源；
3. 记录哪些结论被保留、降格或删除；
4. 只把正文实际引用的来源加入 `book/references.bib`。

## 当前核验日期

本轮编审基准日期：**2026-07-13**。后续发布版本必须更新该日期，并记录新增或改变结论的来源。
