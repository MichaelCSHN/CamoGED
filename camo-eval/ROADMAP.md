# camo-eval ROADMAP / 整改清单

> 所有者：Claude（项目主管）。本文件跟踪 camo-eval 从 Codex 接手后的整改与扩展。
> 基线审计：分支 `wp-a/detection-metrics`（`f792b00`）—— 检测主链路 + CLI + protocols +
> instance/perceptual/signature/video/background 指标 + HF Space + Colab + 合成示例数据，**真实可跑、可视化可用**；
> 41 测试通过、覆盖率 87%、ruff 通过。以下为接手后的待办。

## P0 — 门禁与一致性（立即）
- [ ] **black 失败**：`src/camo_eval/protocols/schema.py` 未格式化（`black --check .` 红）。运行 `black` 修复。
- [ ] **`[generation]` extra 仍不存在**：`metrics/generation/fid.py` 报错信息让用户 `pip install camo-eval[generation]`，但 `pyproject.toml` 只有 `full`/`dev`。补 `generation` extra（torch/clean-fid/lpips 等）或修正报错信息。
- [ ] **冻结清单未覆盖新公开函数**：`scripts/check_api.py` 的 EXPECTED 未含 `iou/dice/boundary_iou/ssim/ms_ssim/precision/recall/precision_recall_curve/video.*/signature.*/background.*`。把新稳定 API 纳入清单以防漂移。

## P1 — 新指标的数值对标（DoD 要求 ≤1e-4，目前缺）
新指标仅有"完美重合"健全性测试，缺权威参照对标：
- [ ] `ssim`/`ms_ssim` 对标 `skimage.metrics`/`torchmetrics`（注意 `ms_ssim` 当前是简化近似，需替换为标准实现或在文档显式标注偏差）。
- [ ] `iou`/`dice` 对标 `torchmetrics`/`sklearn`。
- [ ] `boundary_iou`：当前实现是"边界像素带匹配"，**与 Cheng 2021 的 Boundary IoU（带内区域 IoU）语义不同**。要么对齐标准定义，要么改名避免误导，并固化参照值。
- [ ] `video.j_and_f`/`boundary_f` 对标 DAVIS 官方评测脚本。

## P2 — 补齐缺失的指标簇（按"务实分层"，见 EVAL_SUITE 规划）
- [ ] **生成簇真实实现**：FID/KID/LPIPS/DISTS/(FVD)（`[generation]` extra，torch）。当前全为 stub。
- [ ] **边缘破坏簇**：GabRat / DisRat（Gabor，对标 GabRat-R）。
- [ ] **杂乱度/显著性簇**：Feature Congestion、Subband Entropy、Edge Density、谱残差显著性。
- [ ] **隐蔽/鲁棒下游**：deception_rate/ASR/AP-drop/transferability 配一个自带轻量 judge 检测器，做到"原图 vs 伪装图"实跑。
- [ ] **COD SOTA 专属**：HCE（Qin 2022）、伪装难度排序 + 注视预测（NSS/CC/SIM/AUC，Lv 2021 CAM-LDR）、CIS 的 AP/AP50/AP75。
- [ ] **进阶（诚实层）**：高光谱 RX/CEM/SAM/SID（自带 mini-HSI）；Johnson/TTP/DRI（公式 + 合成输入 + "模型非测量"标注）；行为分析器（实验日志 CSV → d′/ROC/survival）。

## P3 — Demo 与数据
- [ ] HF Space 按簇扩展为多标签页 + 复选框比较（已有 CheckboxGroup 雏形）。
- [ ] `scripts/fetch_examples.py`：按需下载少量真实 COD 样本（COD10K/CAMO/NC4K）与 mini-HSI，**只链接不入库**（守 AGENTS.md 零再分发）。
- [ ] README 状态表与 ARCHITECTURE 随实现推进更新。
