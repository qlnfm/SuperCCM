from skimage.morphology import skeletonize
import numpy as np
import cv2

from superccm.impl.utils.tools import get_split_label, set_edge, get_edge
from superccm.impl.utils.prune import prune

EDGE_THRESH = 20
EDGE_THRESH_RATIO = 0.05
EDGE_MIN_LENGTH = 15
CENTER_MIN_LENGTH = 75
PRUNE_THRESH = 5


def _skeletonize_255(image: np.ndarray) -> np.ndarray:
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255
    return skeleton


def get_skeleton(
        binary_image: np.ndarray,
        mask: np.ndarray,
        um_pixel_ratio: float,
) -> np.ndarray:
    skeleton = _skeletonize_255(binary_image)
    h, w = binary_image.shape[:2]
    avg_hw = (h + w) / 2
    edge_canvas = get_edge(mask, int(avg_hw * EDGE_THRESH_RATIO))
    # Filter discrete short segments/过滤离散短小片段
    for label in get_split_label(skeleton, 2):
        # If one is at the periphery/如果处于边缘
        length = cv2.countNonZero(label)
        in_edge = np.any(cv2.bitwise_and(label, edge_canvas))
        if in_edge and length < EDGE_MIN_LENGTH * um_pixel_ratio:
            skeleton -= label
        # If not/如果不是
        if not in_edge and length < CENTER_MIN_LENGTH * um_pixel_ratio:
            skeleton -= label

    # Remove burrs/去除毛刺
    skeleton = prune(skeleton, PRUNE_THRESH * um_pixel_ratio)

    # Set the edge pixels to 0 by 1 unit/设置边缘1像素为 0
    skeleton = set_edge(skeleton, 1, 0)

    return skeleton
