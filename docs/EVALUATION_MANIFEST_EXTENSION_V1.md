# 评价协议 Manifest 扩展 v1.0

状态：`PROTOCOL-DRAFT`。这些字段面向第16—20章的退化、可靠性、黑箱和污染审计；并不表示 `camo-eval` 核心API已经实现全部字段。

## 最小扩展

```yaml
protocol_id: detectability-eval-v1
implementation_version: null
dataset_version: null
dataset_hashes: []
prediction_revision: null
prediction_hashes: []
environment:
  python: null
  os: null
  dependency_lock: null
  container_image: null
  container_digest: null
severity_factors:
  target_scale:
    raw_symbol: a
    raw_measure: sqrt_pixel_area
    transform_id: log_scale_decreasing_v1
    transform_parameters: {}
    scan_range: []
    direction: higher_z_is_more_degraded
reference_distribution:
  id: P_star_v1
  source_manifest_hash: null
  weighting: uniform_or_registered
responses:
  positive: Y_plus
  negative_correct_rejection: Y_minus
  false_positive_count: N_FP
operating_points:
  native: true
  matched_false_alarm: null
uncertainty:
  method: scene_cluster_bootstrap
  confidence_level: 0.95
pollution_audit:
  model_knowledge_cutoff: unknown
  dataset_publication_date: null
  known_overlap: unknown
  private_holdout: false
query_budget:
  provider: null
  model_version: null
  max_calls: null
  max_cost: null
  retry_policy: null
```

## 哈希与可重建性

- 数据清单、划分、预测和协议文件分别计算SHA-256；
- 记录依赖锁文件和容器镜像digest；
- API模型保存请求日期、模型版本、prompt和原始响应；
- 不把浮动标签的容器镜像视为冻结环境；
- 报告可从原始响应重新生成，而不是只保存最终表格。

## 环境冻结建议

优先级从高到低：

1. 容器镜像digest + 依赖锁文件；
2. Conda/uv/pip-tools锁文件 + OS/驱动信息；
3. 仅`requirements.txt`，但必须固定直接和传递依赖版本；
4. 只写软件名称不满足正式复现要求。

Docker示例只说明冻结方式，不保证所有GPU/传感器实验可在容器内完整复现：

```dockerfile
FROM python:3.11-slim@sha256:<digest>
COPY requirements-lock.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-lock.txt
WORKDIR /workspace
COPY . /workspace
```

## 污染和预算

污染审计记录“已知、疑似、未知、低风险、私有隔离”状态；无法核实模型截止日期时保持`unknown`。查询预算是协议的一部分，任何预算变更若改变模型、prompt、重复数或抽样设计，都需要新的protocol revision。
