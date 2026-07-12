import numpy as np
import pytest

from camo_eval import (
    boundary_f_score,
    boundary_iou,
    dists,
    fid,
    j_and_f,
    kid,
    lpips,
    ms_ssim,
)


def test_unvalidated_standard_names_do_not_return_surrogates(tmp_path):
    image = np.zeros((16, 16), dtype=float)
    for function, args in [
        (boundary_iou, (image, image)),
        (ms_ssim, (image, image)),
        (boundary_f_score, (image[None], image[None])),
        (j_and_f, (image[None], image[None])),
        (lpips, (image, image)),
        (dists, (image, image)),
    ]:
        with pytest.raises(NotImplementedError):
            function(*args)

    real = tmp_path / "real"
    fake = tmp_path / "fake"
    real.mkdir()
    fake.mkdir()
    for function in (fid, kid):
        with pytest.raises(NotImplementedError):
            function(str(real), str(fake))
