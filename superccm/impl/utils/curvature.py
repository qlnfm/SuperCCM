import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d

from networkx import MultiGraph


def find_end_point(points, neighbor_threshold=1.5):
    """
    在一组离散坐标中找到8邻域只有1个邻居的端点。
    neighbor_threshold：判断相邻点的最大距离（像素单位）
    """
    n = len(points)
    if n <= 2:
        return points[0]

    # 计算距离矩阵
    dist = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=2)
    # 邻居条件（排除自己）
    neighbors = (dist < neighbor_threshold) & (dist > 0)

    # 每个点的邻居数量
    neighbor_count = neighbors.sum(axis=1)

    # 找出邻居数为1的点（端点）
    end_indices = np.where(neighbor_count == 1)[0]

    if len(end_indices) > 0:
        return points[end_indices[0]]  # 取第一个端点
    else:
        # 没有明确端点 → 默认第一个
        return points[0]


def sort_line_by_nearest(points, start_point=None):
    """
    使用最近邻算法对一组点排序。
    若未指定起点，则自动检测8邻域端点。
    """
    points = np.asarray(points)
    n = len(points)
    if n <= 2:
        return points

    if start_point is None:
        start_point = find_end_point(points)

    # 初始化排序
    ordered = [start_point]
    remaining = points.tolist()
    remaining.remove(start_point.tolist())

    while remaining:
        last = np.array(ordered[-1])
        dists = np.linalg.norm(np.array(remaining) - last, axis=1)
        nearest_idx = np.argmin(dists)
        ordered.append(remaining.pop(nearest_idx))

    return np.array(ordered)


def merge_lines_with_point(line1, point, line2):
    """
    综合版：
    - 对每条线内部基于8邻域排序
    - 自动判断方向（谁朝向point）
    - 拼接 line1 + point + line2
    """
    line1_sorted = sort_line_by_nearest(line1)
    line2_sorted = sort_line_by_nearest(line2)
    point = np.asarray(point)

    # 判断 line1 是否需要反转
    if np.linalg.norm(line1_sorted[0] - point) < np.linalg.norm(line1_sorted[-1] - point):
        line1_sorted = line1_sorted[::-1]

    # 判断 line2 是否需要反转
    if np.linalg.norm(line2_sorted[-1] - point) < np.linalg.norm(line2_sorted[0] - point):
        line2_sorted = line2_sorted[::-1]

    # 拼接成完整路径
    merged_path = np.concatenate([line1_sorted, point[None, :], line2_sorted], axis=0)
    return merged_path


def resample_path(points, step=1.0, sort_points=True):
    """按固定弧长间隔重采样路径"""
    points = np.asarray(points)
    diffs = np.diff(points, axis=0)
    seg_len = np.linalg.norm(diffs, axis=1)
    s = np.concatenate([[0], np.cumsum(seg_len)])
    new_s = np.arange(0, s[-1], step)
    fx = interp1d(s, points[:, 0], kind='linear')
    fy = interp1d(s, points[:, 1], kind='linear')
    return np.stack([fx(new_s), fy(new_s)], axis=1), new_s


def smooth_path(path, sigma=1.0):
    """高斯平滑路径坐标"""
    if sigma <= 0:
        return path
    return np.stack([
        gaussian_filter1d(path[:, 0], sigma=sigma),
        gaussian_filter1d(path[:, 1], sigma=sigma)
    ], axis=1)


def discrete_curvature(path, step=1.0):
    """使用中心差分公式计算离散曲率"""
    x, y = path[:, 0], path[:, 1]
    dx = np.gradient(x, step)
    dy = np.gradient(y, step)
    ddx = np.gradient(dx, step)
    ddy = np.gradient(dy, step)
    kappa = np.abs(dx * ddy - dy * ddx) / (dx ** 2 + dy ** 2 + 1e-8) ** 1.5
    return kappa


def curvature_at_point(line1, line2, point, step=1.0, sigma=10.0):
    """
    获取指定坐标点处的离散曲率值
    """
    # 1️⃣ 按弧长重采样路径
    merged = merge_lines_with_point(line1, point, line2)
    path_resampled, _ = resample_path(merged, step=step)

    # 2️⃣ 平滑路径（可选）
    path_smooth = smooth_path(path_resampled, sigma=sigma)

    # 3️⃣ 计算曲率
    kappa = discrete_curvature(path_smooth, step=step)

    # 4️⃣ 找到距离目标点最近的重采样点
    target_point = np.asarray(point)
    distances = np.linalg.norm(path_smooth - target_point, axis=1)
    nearest_idx = np.argmin(distances)

    # 5️⃣ 返回对应的曲率值
    return kappa[nearest_idx], nearest_idx


def get_curvature(g: MultiGraph, node: int, uvk1: tuple[int, int, int], uvk2: tuple[int, int, int]) -> float:
    """ 给定一个Node和两条Edge，计算Node处曲率 """
    edge1 = g.get_edge_data(*uvk1)['obj']
    edge2 = g.get_edge_data(*uvk2)['obj']
    node = g.nodes(data=True)[node]['obj']
    kappa, _ = curvature_at_point(edge1.coords, edge2.coords, node.centroid)
    return kappa


if __name__ == '__main__':
    from tools import get_coordinates, get_split_label
    import cv2
    import superccm

    img = cv2.imread('1.bmp', 0)
    line1 = line2 = point = None
    for label in get_split_label(img):
        if cv2.countNonZero(label) == 1:
            point = get_coordinates(label)[0]
            print(point)
        else:
            if line1 is None:
                line1 = get_coordinates(label)
            else:
                line2 = get_coordinates(label)
    merged = merge_lines_with_point(line1, point, line2)
    path, s = resample_path(merged)
    paths = smooth_path(path, sigma=0.0)
    kappa = discrete_curvature(paths)
    print(max(kappa))
    print(curvature_at_point(line1, line2, point, sigma=0.0))
    # canvas = superccm.api.get_canvas(1)

    # 转成整数像素坐标
    img = np.zeros_like(img)
    pts = paths.astype(int)

    # 防止越界（例如坐标落在图像外面）
    h, w = img.shape
    pts = pts[(pts[:, 0] >= 0) & (pts[:, 0] < w) &
              (pts[:, 1] >= 0) & (pts[:, 1] < h)]

    # 注意：OpenCV 图像是 (row, col) = (y, x)
    img[pts[:, 1], pts[:, 0]] = 255
    superccm.api.show_image(img)
