import onnxruntime
import numpy as np
import cv2
from skimage.measure import label
from skimage.morphology import skeletonize

from typing import Union, Sequence

CCM_IMAGE_SHAPE = (384, 384)


def save_image(image, path='result.png'):
    """ Save an image """
    extend = '.' + path.split('.')[-1]
    retval, buffer = cv2.imencode(extend, image.astype('uint8'))
    with open(path, 'wb') as f:
        f.write(buffer)


def show_image(image):
    """ Show an image """
    image_show = image.copy().astype('uint8')
    if np.amax(image_show) == 1:
        image_show = image_show * 255
    cv2.imshow('Show', image_show)
    cv2.waitKey(0)


def get_canvas(channels=1, hw: tuple[int, int] = CCM_IMAGE_SHAPE):
    """ Obtain a canvas with a size of 0 pixels """
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
    :param image: Binary image
    :param connectivity: connectivity=1 uses 4-connectivity; connectivity=2 uses 8-connectivity
    :return: A list consisting of N binary images, where N represents the number of connected regions.
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

    point_set = set(points)
    visited = set()

    start = next(iter(point_set))
    stack = [start]
    visited.add(start)

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # DFS
    while stack:
        x, y = stack.pop()
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if neighbor in point_set and neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)

    return len(visited) == len(point_set)


def cal_length(canvas: np.ndarray) -> float:
    """ Calculate the length of the curve's pixels """
    length = 0
    contours, _ = cv2.findContours(canvas, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        length += cv2.arcLength(c, True) / 2
    return length
