from skimage.morphology import skeletonize
import numpy as np
import cv2

from superccm.impl.utils.tools import get_split_label, get_canvas
from superccm.impl.utils.prune import prune


def _skeletonize_255(image: np.ndarray) -> np.ndarray:
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255
    return skeleton


def _set_edge(canvas: np.ndarray, x: int, value: int) -> np.ndarray:
    canvas[:x, :] = value  # 上边
    canvas[-x:, :] = value  # 下边
    canvas[:, :x] = value  # 左边
    canvas[:, -x:] = value  # 右边
    return canvas


EDGE_CANVAS = _set_edge(get_canvas(1), 10, 255)


def get_skeleton(
        binary_image: np.ndarray,
        min_length: int = 75,
        min_length_edge: int = 15,
        prune_thresh: int = 5
) -> np.ndarray:
    skeleton = _skeletonize_255(binary_image)
    # 过滤离散短小片段
    for label in get_split_label(skeleton, 2):
        # 如果处于边缘
        length = cv2.countNonZero(label)
        in_edge = np.any(cv2.bitwise_and(label, EDGE_CANVAS))
        if in_edge and length < min_length_edge:
            skeleton -= label
        # 如果不是
        if not in_edge and length < min_length:
            skeleton -= label

    # 去除毛刺
    skeleton = prune(skeleton, prune_thresh)

    # 设置边缘 x 像素为 0
    skeleton = _set_edge(skeleton, 1, 0)

    return skeleton
