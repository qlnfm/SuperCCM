from ..impl.segment import segment
from ..impl.skeleton.skeletonize import get_skeleton
from ..impl.topology.graphify import graphify
from ..impl.metircs.metrics import get_metrics
from ..impl.io.read import read_image

import numpy as np

segmenter = segment.CornealNerveSegmenter()


def analysis(image_input) -> dict[str, float]:
    image = read(image_input)
    binary = seg(image)
    skeleton = skel(binary)
    graph = grfy(image, binary, skeleton)
    metrics = meas(graph)
    return metrics


def read(image_input) -> np.ndarray:
    return read_image(image_input)


def seg(image: np.ndarray, *, post_process=True) -> np.ndarray:
    if not image.shape == (384, 384):
        raise TypeError('This method is expected to input a grayscale image with a size of 384*384.')
    return segmenter(image, post_process=post_process)


def skel(image: np.ndarray) -> np.ndarray:
    if not np.isin(image, [0, 255]).all():
        raise ValueError('This method is expected to receive binary images composed solely of 0s and 255s as input.')
    return get_skeleton(image)


def grfy(image: np.ndarray, binary_image: np.ndarray, skeleton_image: np.ndarray):
    return graphify(image, binary_image, skeleton_image)


def meas(n_graph, digit=3) -> dict[str, float]:
    return get_metrics(n_graph, digit)
