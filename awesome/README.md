# Awesome Camouflage [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated, cross-domain list of resources on camouflage — **generation, detection, and
> evaluation** — across **Nature · War · Machines** and the **physical · digital · intelligent**
> domains.
>
> Organized around one thesis: camouflage is a *co-evolutionary game* between a **hider**
> (generation) and a **seeker** (detection), refereed by **evaluation**.

> **Maintained as part of [CamoGED](../README.md).** Most entries are generated from
> [`data/papers.yaml`](../data/papers.yaml) and [`data/datasets.yaml`](../data/datasets.yaml) —
> please add resources there (see [CONTRIBUTING](../CONTRIBUTING.md)).

## Contents

- [Books, Monographs & Theses](#-books-monographs--theses)
- [Surveys & Foundational Papers](#-surveys--foundational-papers)
- [Natural Camouflage](#-natural-camouflage)
- [Military Camouflage](#-military-camouflage)
- [Camouflage in Art & Culture](#-camouflage-in-art--culture)
- [Generation (the hider)](#️-generation-the-hider)
- [Detection (the seeker)](#-detection-the-seeker)
- [Evaluation (the judge)](#-evaluation-the-judge)
- [Our Research Projects](#-our-research-projects)
- [Demos, Tools & Tutorials](#-demos-tools--tutorials)
- [Workshops, Challenges & Venues](#️-workshops-challenges--venues)
- [Acknowledgements & Related Lists](#-acknowledgements--related-lists)

---

## 📖 Books, Monographs & Theses

*A category no existing camouflage list maintains. PRs welcome.*

- **CamoGED Monograph** — *Camouflage: Generation, Detection & Evaluation* (this project) — [book](../book/)

## 🧭 Surveys & Foundational Papers

- **A Survey of Camouflaged Object Detection and Beyond** — Xiao et al., *CAAI AIR* 2024. [paper](https://arxiv.org/abs/2408.14562)
- *(biology)* Ruxton, Allen, Sherratt & Speed — *Avoiding Attack: The Evolutionary Ecology of Crypsis, Warning Signals and Mimicry*
- *(military/biology)* **Cultural evolution of military camouflage** — *Phil. Trans. R. Soc. B* 2017. [paper](https://royalsocietypublishing.org/doi/10.1098/rstb.2016.0351)

## 🌿 Natural Camouflage

- Mechanisms: crypsis, disruptive coloration, countershading, masquerade, mimicry
- Recommended entry path: Cott (1940) → Stevens & Merilaita reviews → modern coloration studies

## 🪖 Military Camouflage

- Historical pattern genealogy (WWI French camouflage → digital/pixel patterns)
- Multispectral / IR / radar / terahertz stealth
- Military deception (MILDEC) and decoys

## 🎨 Camouflage in Art & Culture

- Trompe-l'œil; dazzle camouflage; camouflage in fashion and fine art

## ✍️ Generation (the hider)

### Physical adversarial camouflage
- **PhyCamo** — multi-view physical adversarial camouflage via contrastive learning, *AAAI* 2025. [paper](https://doi.org/10.1609/aaai.v39i10.33110)
- **CAM3D** — cross-domain 3D adversarial camouflage (Mamba-enhanced), 2025. [paper](https://www.mdpi.com/2079-9292/14/19/3868)
- Lineage: DAS → FCA → DTA → ACTIVE → RAUCA

### Digital adversarial & steganography & deepfake
- AdvCam (natural-style adversarial), unrestricted adversarial examples, diffusion-based stealthy attacks

### Generative models for camouflage
- **CamDiff** — diffusion-based camouflage image augmentation, *CAAI AIR* 2023. [paper](https://www.sciopen.com/article/10.26599/AIR.2023.9150021)
- SCODE — synthetic camouflage data to boost detection

## 🔎 Detection (the seeker)

### Datasets
See the full table in [`data/datasets.yaml`](../data/datasets.yaml) (COD10K, CAMO, NC4K, MoCA-Mask,
CamoVid60K, MCOD, MM-CamObj, and more).

### Image COD
- **ZoomNeXt** — unified collaborative pyramid network, *TPAMI* 2024.
- **HGINet** — hierarchical graph interaction, *IEEE TIP* 2024.

### Video COD
- **When SAM2 Meets VCOS** — comprehensive evaluation & adaptation, 2025. [paper](https://arxiv.org/abs/2409.18653)
- **CamoSAM2** — motion-appearance auto-refining prompts, 2025. [paper](https://arxiv.org/abs/2504.00375)

### Instance segmentation / counting / ranking
- Camouflaged instance segmentation; simultaneous localize-segment-rank

### Extended tasks
- Referring COD (R2C7K); Collaborative COD (CoCOD8K); Open-Vocabulary COS

### Foundation-model adaptations
- SAM/SAM2 adapters, dual-stream adapters; CLIP zero-shot; DINOv2/v3; MLLM × camouflage

### Multispectral / IR / polarization / remote sensing
- MCOD (multispectral); polarization-guided COD; remote-sensing camouflage

## 📊 Evaluation (the judge)

- Detection metrics & toolkits: S-measure, weighted F-measure, E-measure, MAE → see [`camo-eval`](../camo-eval/)
- Generation metrics: FID, LPIPS, deception rate
- Robustness metrics: attack success rate, AP drop, transferability
- Public leaderboards & human-perception studies

## 🔬 Our Research Projects

- **coder** — image COD ([projects/coder](../projects/coder/))
- **flowcamo** — motion-aware video camouflage generation + detection ([projects/flowcamo](../projects/flowcamo/))
- **dualvcod** — dual-path video camouflage instance detection ([projects/dualvcod](../projects/dualvcod/))

## 🌐 Demos, Tools & Tutorials

- CamoGED website demos (image / video / instance) — *coming soon*
- `camo-eval` toolkit — unified evaluation

## 🏛️ Workshops, Challenges & Venues

- CVPR PVUW workshop (video segmentation tracks), and related concealed-scene challenges

## 🤝 Acknowledgements & Related Lists

This list builds on and complements:

- [visionxiang/awesome-camouflaged-object-detection](https://github.com/visionxiang/awesome-camouflaged-object-detection)
- [ChunmingHe/awesome-concealed-object-segmentation](https://github.com/ChunmingHe/awesome-concealed-object-segmentation)
- [clelouch/Awesome-Camouflaged-Object-Detection](https://github.com/clelouch/Awesome-Camouflaged-Object-Detection)
- [GuoleiSun/Awesome-SAM2](https://github.com/GuoleiSun/Awesome-SAM2)

## Contributing

PRs welcome! Add resources to [`data/`](../data/) and follow [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

[CC-BY-4.0](../LICENSE-CONTENT). Datasets are linked, not redistributed.
