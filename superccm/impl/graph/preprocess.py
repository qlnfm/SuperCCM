import numpy as np

from superccm.impl.utils.histogram_matching import histogram_standardization
from superccm.impl.utils.ccm_vignetting import vignetting_correction
from superccm.impl.utils.prune import prune
from superccm.impl.utils.estimate_width import estimate_width

PRUNE_LENGTH_THRESH = 5


def graphify_preprocess(skeleton: np.ndarray, image: np.ndarray):
    """
    创建MultiGraph之前，对骨架进行预处理:
    1. 直方图规定化和暗角校正，以提取强度分布
    2. 剪枝
    返回:
    处理后的骨架
    """
    image_std = histogram_standardization(image)
    image_vig = vignetting_correction(image_std)
    intensity_map = estimate_width(image_vig, skeleton)
    skeleton_ = prune(skeleton, length_thresh=5)

    return skeleton_, intensity_map
