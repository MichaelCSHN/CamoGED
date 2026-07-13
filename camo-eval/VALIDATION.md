# camo-eval validation register

| Metric/API | Implementation ID | Level | Reference/evidence | Formal reporting allowed? |
|---|---|---|---|---|
| MAE/Fw/Sm/Em/F/PR | `cod-core-pysodmetrics-1` | validated | PySODMetrics comparison tests | yes, with version and protocol |
| SSIM | `ssim-skimage-gaussian-1` | validated | scikit-image comparison | yes, with settings |
| IoU/Dice | `binary-set-1` | validated definition | exact set tests | yes |
| AP/AR helper | `ranked-flags-1` | implemented | unit tests; not COCO evaluator | only with definition stated |
| `edge_density` | `sobel-edge-density-1` | implemented descriptor | explicit threshold rule and bounds tests | only as the documented descriptor |
| `subband_entropy` | `gradient-entropy-proxy-1` | experimental | Sobel-gradient histogram, not a validated subband model | no standard subband-entropy claim |
| `feature_congestion` | `feature-congestion-proxy-1` | experimental | simplified contrast/orientation proxy | no Rosenholtz feature-congestion claim |
| `camouflage_difficulty` | `difficulty-heuristic-1` | experimental | fixed handcrafted weighted summary | no human detectability or benchmark claim |
| `boundary_match_score` | `boundary-match-lite-1` | experimental | known cases only | no standard Boundary IoU claim |
| `ms_ssim_lite` | `ms-ssim-lite-1` | experimental | identity/monotonic tests | no standard MS-SSIM claim |
| `boundary_f_score_lite`/`j_and_f_lite` | `video-boundary-lite-1` | experimental | known cases only | no DAVIS claim |
| `fid_lite`/`kid_lite` | `handcrafted-distribution-lite-1` | experimental | deterministic smoke tests | no FID/KID claim |
| `lpips_lite`/`dists_lite` | `handcrafted-pair-lite-1` | experimental | identity/change tests | no LPIPS/DISTS claim |

A metric moves to `validated` only after a named authoritative implementation or official script is compared over representative and edge-case fixtures, with tolerance and dependency version recorded.
