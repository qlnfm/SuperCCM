from skimage.morphology import skeletonize
import numpy as np
import cv2

from superccm.impl.utils.tools import get_split_label, get_canvas
from superccm.impl.utils.prune import prune

CCM_IMAGE_SHAPE = (384, 384)
EDGE_THRESH = 10
EDGE_MIN_LENGTH = 15
CENTER_MIN_LENGTH = 75
PRUNE_THRESH = 5


def _skeletonize_255(image: np.ndarray) -> np.ndarray:
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255
    return skeleton


def _set_edge(canvas: np.ndarray, x: int, value: int) -> np.ndarray:
    canvas[:x, :] = value  # up
    canvas[-x:, :] = value  # down
    canvas[:, :x] = value  # left
    canvas[:, -x:] = value  # right
    return canvas


EDGE_CANVAS = _set_edge(get_canvas(1), EDGE_THRESH, 255)


def get_skeleton(
        binary_image: np.ndarray,
        min_length: int = CENTER_MIN_LENGTH,
        min_length_edge: int = EDGE_MIN_LENGTH,
        prune_thresh: int = PRUNE_THRESH,
) -> np.ndarray:
    skeleton = _skeletonize_255(binary_image)
    # Filter discrete short segments/过滤离散短小片段
    for label in get_split_label(skeleton, 2):
        # If one is at the periphery/如果处于边缘
        length = cv2.countNonZero(label)
        in_edge = np.any(cv2.bitwise_and(label, EDGE_CANVAS))
        if in_edge and length < min_length_edge:
            skeleton -= label
        # If not/如果不是
        if not in_edge and length < min_length:
            skeleton -= label

    # Remove burrs/去除毛刺
    skeleton = prune(skeleton, prune_thresh)

    # Set the edge pixels to 0 by 1 unit/设置边缘1像素为 0
    skeleton = _set_edge(skeleton, 1, 0)

    return skeleton
