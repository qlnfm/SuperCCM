import superccm
import cv2
import numpy as np
from scipy.ndimage import label, center_of_mass
from .tools import get_split_label, get_coordinates, get_conv2d, get_8_neighbors, is_4_connected, skeletonize_255

CLASSIFY_KERNEL = np.array([
    [1, 1, 1],
    [1, 10, 1],
    [1, 1, 1]
], dtype='uint8')


def neighbors8(y, x, shape):
    """返回8邻域坐标"""
    h, w = shape
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == dx == 0:
                continue
            ny, nx_ = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx_ < w:
                yield ny, nx_


def neighbors4(y, x, shape):
    """返回4邻域坐标"""
    h, w = shape
    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ny, nx_ = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx_ < w:
            yield ny, nx_


def degree(img, y, x):
    """计算8连通邻居中的前景像素数"""
    return sum(img[ny, nx_] > 0 for ny, nx_ in neighbors8(y, x, img.shape))


def extract_true_branch_points(skel, branch_candidates):
    """在每个分支簇中挑选真正分支点（可能多个）"""
    labeled, n = label(branch_candidates)
    true_branches = []

    for i in range(1, n + 1):
        coords = np.argwhere(labeled == i)

        # Step0: 查找同时存在水平和垂直4连通邻居的点
        multi_branch_pts = []
        for y, x in coords:
            up = (y > 0 and skel[y - 1, x] > 0)
            down = (y < skel.shape[0] - 1 and skel[y + 1, x] > 0)
            left = (x > 0 and skel[y, x - 1] > 0)
            right = (x < skel.shape[1] - 1 and skel[y, x + 1] > 0)
            has_vert = up or down
            has_horz = left or right
            if has_vert and has_horz:
                multi_branch_pts.append((y, x))

        if multi_branch_pts:
            # 如果存在多个方向连通的点，则都作为真分支点
            true_branches.extend(multi_branch_pts)
            continue

        # 否则执行原始三步筛选逻辑
        four_counts = [
            sum(skel[ny, nx_] > 0 for ny, nx_ in neighbors4(y, x, skel.shape))
            for y, x in coords
        ]
        max4 = np.max(four_counts)
        cand1 = [coords[j] for j, c in enumerate(four_counts) if c == max4]

        deg_sum = [
            sum(degree(skel, ny, nx_) for ny, nx_ in neighbors8(y, x, skel.shape))
            for y, x in cand1
        ]
        maxdeg = np.max(deg_sum)
        cand2 = [p for p, d in zip(cand1, deg_sum) if d == maxdeg]

        cy, cx = center_of_mass(labeled == i)
        dists = [np.hypot(y - cy, x - cx) for y, x in cand2]
        true_branches.append(tuple(cand2[np.argmin(dists)]))

    true_branches = np.array(true_branches)
    return true_branches


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
    """ Remove burrs from the skeleton """
    while True:
        skeleton_ = _prune(skeleton_image, length_thresh=length_thresh)
        if np.sum(skeleton_) == np.sum(skeleton_image):
            break
        else:
            skeleton_image = skeleton_

    return skeleton_
