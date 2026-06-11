# camo-eval ROADMAP / 整改清单

> 所有者：Claude（项目主管）。本文件跟踪 camo-eval 从 Codex 接手后的整改与扩展。
> 基线审计：分支 `wp-a/detection-metrics`（`f792b00`）—— 检测主链路 + CLI + protocols +
> instance/perceptual/signature/video/background 指标 + HF Space + Colab + 合成示例数据，**真实可跑、可视化可用**；
> 41 测试通过、覆盖率 87%、ruff 通过。以下为接手后的待办。

## P0 — 门禁与一致性（立即）
- [ ] **black 失败**：`src/camo_eval/protocols/schema.py` 未格式化（`black --check .` 红）。运行 `black` 修复。
- [ ] **`[generation]` extra 仍不存在**：`metrics/generation/fid.py` 报错信息让用户 `pip install camo-eval[generation]`，但 `pyproject.toml` 只有 `full`/`dev`。补 `generation` extra（torch/clean-fid/lpips 等）或修正报错信息。
- [x] **冻结清单覆盖新公开函数**：`scripts/check_api.py` 新增 `EXTENSION` 段，冻结 `precision/recall/precision_recall_curve/iou/dice/boundary_iou/average_precision/average_recall/ssim/ms_ssim/signature.*/background.*/video.*` 的签名，防漂移。

## P1 — 新指标的数值对标（DoD 要求 ≤1e-4）
- [x] `ssim` 对标 `skimage.metrics`（已对齐高斯加权 + 边界裁剪约定，≤1e-4，见 `tests/test_reference_metrics.py`）。
- [x] `iou`/`dice` 在二值掩码上对精确集合定义（`tests/test_reference_metrics.py`）。
- [~] `ms_ssim`：当前仍是简化近似（逐尺度全图 SSIM 连乘，缺逐尺度 cs/亮度分离），暂以恒等+单调性回归测试守住；标准实现（对标 `torchmetrics`，需 torch）留待 P2。
- [~] `boundary_iou`：已固化已知用例并在文档/测试中明确**这是带容差的边界像素匹配，非 Cheng 2021 区域带 Boundary IoU**。后续考虑新增独立的标准实现（不改现有公开名以免破坏 API）。
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
