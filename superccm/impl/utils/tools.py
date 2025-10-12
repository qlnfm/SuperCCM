import onnxruntime
import numpy as np
import cv2
from skimage.measure import label
from skimage.morphology import skeletonize

from typing import Union, Sequence


def get_canvas(channels=1, hw: tuple[int, int] = (384, 384)):
    """ 获取一张空画布图像 """
    if channels > 1:
        return np.zeros([*hw, channels], dtype='uint8')
    return np.zeros(hw, dtype='uint8')


def skeletonize_255(image: np.ndarray) -> np.ndarray:
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255
    return skeleton


def get_conv2d(image, kernel):
    assert len(image.shape) == 2
    output = cv2.filter2D(image, -1, kernel)
    return output


def get_split_label(image, connectivity=2):
    """
    :param image: 二值化图像
    :param connectivity: connectivity=1 使用 4-连通;connectivity=2 使用 8-连通
    :return: N(连通区域个数)个二值化图像组成的列表
    """
    image_ = image.copy()
    image_[image > 0] = 1
    labels, num = label(image_, connectivity=connectivity, return_num=True)

    segments = []
    for i in range(1, num + 1):
        component_image = np.where(labels == i, 1, 0)
        component_image = component_image * 255
        component_image = component_image.astype('uint8')
        segments.append(component_image)

    return segments


def get_coordinates(image, value: Union[int, Sequence] = 255) -> list[tuple[int, int]]:
    """
    Get the coordinate group in the image whose value is the specified value
    :param image: Grayscale image
    :param value: The values or groups of values to be obtained
    :return: A coordinate group that meets the conditions
    """
    if isinstance(value, int):
        value = [value]
    coordinates = []
    for v in value:
        ys, xs = np.where(image == v)
        coords = np.stack((xs, ys), axis=-1)  # shape: (N, 2)
        coordinates_list = [tuple(int(n) for n in coord) for coord in coords]
        coordinates.extend(coordinates_list)
    return coordinates


def get_dilate(image, size=3, iterations=1):
    """ Perform the expansion operation """
    kernel = np.ones((size, size), np.uint8)
    dilated = cv2.dilate(image, kernel, iterations=iterations)
    return dilated


def get_4_neighbors(x, y):
    """Obtain a coordinate group of 4 neighborhoods (up, down, left, right) around a coordinate"""
    return [
        (x + dx, y + dy)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
    ]


def get_8_neighbors(x, y):
    """ Obtain a coordinate group of 8 neighborhoods around a coordinate """
    return [
        (x + dx, y + dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if not (dx == 0 and dy == 0)
    ]


def is_4_connected(points):
    if not points:
        return False

    # 用集合加速查找
    point_set = set(points)
    visited = set()

    # 任取一个起点
    start = next(iter(point_set))
    stack = [start]
    visited.add(start)

    # 四联通方向
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # DFS
    while stack:
        x, y = stack.pop()
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if neighbor in point_set and neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)

    # 判断是否所有点都访问到
    return len(visited) == len(point_set)
