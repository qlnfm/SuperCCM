import numpy as np
import cv2
from scipy.ndimage import label

from typing import Literal, Union, Sequence

from superccm.modules.common import get_canvas
from .component import SkeletonComponent

CLASSIFY_KERNEL = np.array([
    [1, 1, 1],
    [1, 10, 1],
    [1, 1, 1]
], dtype='uint8')
STRUCTURE_4 = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]])

STRUCTURE_8 = np.array([[1, 1, 1],
                        [1, 1, 1],
                        [1, 1, 1]])


class NerveImage:
    def __init__(self, image: np.ndarray, binary_image: np.ndarray, skeleton_image: np.ndarray):
        self.image = image.copy()

        self.binary = binary_image
        self.skeleton = skeleton_image

        self.weighted_skeleton = None

        # background: 0, endpoint: 1, branch_point: 2, edge: 3, edge_endpoint: 4
        self.classified_skeleton = get_canvas()
        self.edges: dict[int, SkeletonComponent] = {}
        self.nodes: dict[int, SkeletonComponent] = {}

        self.process()
        self.find_neighbors()
        self.assign_weights()

    def process(self):
        classified = get_conv2d(self.skeleton // 255, CLASSIFY_KERNEL)
        edges_mask, nodes_mask = classified == 12, np.isin(classified, (11, *tuple(range(13, 19))))
        edges, nodes = get_canvas(), get_canvas()
        edges[edges_mask] = 255
        nodes[nodes_mask] = 255
        classified_edges = get_conv2d(edges // 255, CLASSIFY_KERNEL)

        self.classified_skeleton[classified == 11] = 1
        self.classified_skeleton[classified == 12] = 3
        self.classified_skeleton[classified >= 13] = 2
        self.classified_skeleton[np.isin(classified_edges, (10, 11))] = 4

        edges_num, edges_labels = get_componentes(edges)
        for i in range(1, edges_num):
            coords = get_coordinates(edges_labels, i)
            edge = SkeletonComponent('edge', i, coords)
            bone = get_canvas()
            for x, y in coords:
                bone[y, x] = 255
            edge.bone = bone
            edge.body = get_deconvolution(self.binary, bone)
            self.edges[i] = edge

        nodes_num, nodes_labels = get_componentes(nodes)
        for i in range(1, nodes_num):
            coords = get_coordinates(nodes_labels, i)
            node = SkeletonComponent('node', i, coords)
            bone = get_canvas()
            for x, y in coords:
                bone[y, x] = 255
            node.bone = bone
            self.nodes[i] = node

    def find_neighbors(self):
        """ Find the two nodes adjacent to each edge """
        edge_endpoints = get_coordinates(self.classified_skeleton, 4)
        for idx, edge in self.edges.items():
            endpoints = [coord for coord in edge.coords if coord in edge_endpoints]
            neighbor_points = [p for ep in endpoints for p in get_8_neighbors(*ep)]
            for p in neighbor_points:
                for node in self.nodes.values():
                    if p in node.coords:
                        self.edges[idx].neighbors.append(node.index)

    def assign_weights(self):
        """ Assign the width weight for each edge """
        # gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        conv_result = get_conv2d(self.image, get_gaussian_kernel())
        conv_result[self.skeleton == 0] = 0
        normalized_result = get_normalized(conv_result)
        self.weighted_skeleton = normalized_result

        for _, edge in self.edges.items():
            for x, y in edge.coords:
                edge.weights.append(int(self.weighted_skeleton[y, x]))


def get_gaussian_kernel(ksize=5, sigma=1):
    """ Get a Gaussian kernel """
    gaussian_kernel = cv2.getGaussianKernel(ksize=ksize, sigma=sigma)
    gaussian_kernel_2d = gaussian_kernel @ gaussian_kernel.T
    return gaussian_kernel_2d


def get_componentes(image, connectivity: Literal[4, 8] = 8):
    """
    Get all the connected regions and their numbers
    :param image: The input binary image is a uint8 np.ndarray composed of 0 and 255
    :param connectivity: The connectivity judgment method is either 4 or 8
    :return: (Number of connectivity regions, Connectivity label matrix)
    """
    assert np.all(((image == 0) | (image == 255))) and image.dtype == np.uint8
    image = image // 255
    num_labels, labels = cv2.connectedComponents(image, connectivity=connectivity)
    return num_labels, labels


def get_conv2d(image, kernel):
    assert len(image.shape) == 2
    output = cv2.filter2D(image, -1, kernel)
    return output


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


def get_8_neighbors(x, y):
    """ Obtain a coordinate group of 8 neighborhoods around a coordinate """
    return [
        (x + dx, y + dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if not (dx == 0 and dy == 0)
    ]


def get_normalized(image):
    """ Standardize the non-zero areas of the grayscale image to between 1 and 255 """
    mask = image > 0
    values = image[image > 0]
    min_val, max_val = np.min(values), np.max(values)
    normalized = np.zeros_like(image, dtype=np.uint8)

    if max_val > min_val:
        scaled = ((image[mask] - min_val) / (max_val - min_val) * 254) + 1
        normalized[mask] = scaled.astype(np.uint8)
    else:
        normalized[mask] = 255

    return normalized


def get_dilate(image, size=3, iterations=1):
    """ Perform the expansion operation """
    kernel = np.ones((size, size), np.uint8)
    dilated = cv2.dilate(image, kernel, iterations=iterations)
    return dilated


def get_close(image, size=3):
    """ Perform the closing operation """
    kernel = np.ones((size, size), np.uint8)
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return closing


def get_deconvolution(binary, skeleton, threshold=3):
    """ Deconvolution is performed through distance transformation """

    def split(image):
        image = image > 0
        arrays, num = label(image, structure=STRUCTURE_4)

        segments = []
        for i in range(1, num + 1):
            component_image = np.where(arrays == i, 1, 0)
            component_image = component_image * 255
            component_image = component_image.astype('uint8')
            segments.append(component_image)

        return segments, num

    skeleton = skeleton > 0
    skeleton = skeleton.astype('bool')

    dist_transform = cv2.distanceTransform((1 - skeleton).astype(np.uint8), cv2.DIST_L2, 5)
    distance_threshold = threshold
    selected_pixels = (dist_transform <= distance_threshold) & binary

    segments, num = split(selected_pixels)
    if num == 1:
        return selected_pixels
    else:
        areas = [cv2.countNonZero(s) for s in segments]
        return segments[np.argmax(areas)]
