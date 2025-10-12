import superccm
import cv2
import numpy as np
from .branch_point import extract_true_branch_points
from .tools import get_split_label, get_coordinates, get_conv2d, get_8_neighbors, is_4_connected, skeletonize_255

CLASSIFY_KERNEL = np.array([
    [1, 1, 1],
    [1, 10, 1],
    [1, 1, 1]
], dtype='uint8')


def _prune(skeleton_image, length_thresh=5):
    skeleton_image = skeleton_image.copy()
    skeleton_cls = get_conv2d(skeleton_image / 255, CLASSIFY_KERNEL)

    # 查找真分支点像素
    branch_points = extract_true_branch_points(skeleton_image, skeleton_cls >= 13)
    canvas_bp = superccm.api.get_canvas(1)
    for r, c in branch_points:
        canvas_bp[r, c] = 255

    # 端点像素
    canvas_ep = superccm.api.get_canvas(1)
    canvas_ep[skeleton_cls == 11] = 255
    # coords_ep = get_coordinates(skeleton_cls, 11)

    # 去除短分支
    skeleton_ = skeleton_image.copy()
    canvas = superccm.api.get_canvas(1)
    canvas[skeleton_cls == 12] = 255
    canvas[skeleton_cls == 11] = 255
    canvas[canvas_bp > 0] = 0
    # 含有端点的线段，小于length_thresh的被移除
    labels = get_split_label(canvas)
    for label in labels:
        nz_num = cv2.countNonZero(label)
        ep_overlay = np.any(label & canvas_ep)
        if ep_overlay and nz_num < length_thresh:
            skeleton_[label > 0] = 0

    # 中间像素判定(degree >= 3 and not a true branch point)
    canvas_mid = superccm.api.get_canvas(1)
    canvas_mid[skeleton_cls >= 13] = 255
    canvas_mid = canvas_mid - canvas_bp
    for coord in get_coordinates(canvas_mid):
        neighbors = get_8_neighbors(*coord)
        # 周围骨架像素全部4连通
        neighbors = [(x, y) for x, y in neighbors if skeleton_[y, x]]
        if is_4_connected(neighbors):
            x, y = coord
            skeleton_[y, x] = 0

    return skeletonize_255(skeleton_)


def prune(skeleton_image, length_thresh=5):
    """ 骨架去毛刺 """
    while True:
        skeleton_ = _prune(skeleton_image, length_thresh=length_thresh)
        if np.sum(skeleton_) == np.sum(skeleton_image):
            break
        else:
            skeleton_image = skeleton_

    return skeleton_
