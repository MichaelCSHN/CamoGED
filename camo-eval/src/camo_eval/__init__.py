"""camo-eval: unified evaluation toolkit for camouflage research.

Three families of metrics:
  - detection : Sm, Fw, Em, MAE (image/video camouflaged object detection)
  - generation: FID, LPIPS, deception_rate (camouflage / adversarial synthesis quality)
  - robustness: attack success rate, AP drop, transferability

Only MAE ships as a fully working reference implementation in v0.1.0; the rest are
scaffolded with clear TODOs and consistent signatures so contributors can fill them in.
"""

from .metrics.detection.mae import mae

__version__ = "0.1.0"
__all__ = ["mae", "__version__"]
