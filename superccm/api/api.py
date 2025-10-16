from superccm.impl.segment import segment
from superccm.impl.skeleton.skeletonize import get_skeleton
from superccm.impl.trunk.extract_trunk import extract_trunk
from superccm.impl.graph.graphify import graphify
from superccm.impl.graph.vis import vis_ACCM
from superccm.impl.metircs.metrics import get_metrics
from superccm.impl.io.read import read_image
from superccm.impl.utils.histogram_matching import histogram_standardization
from superccm.impl.utils.ccm_vignetting import vignetting_correction
from superccm.impl.utils.estimate_width import estimate_width

import numpy as np
import cv2
import networkx as nx

segmenter = segment.CornealNerveSegmenter()


def analysis(image_or_path) -> dict[str, float]:
    image = read(image_or_path)
    binary = seg(image)
    skeleton = skel(binary)
    trunks = trunk(image, skeleton)
    graph = grfy(image, skeleton, trunks)
    metrics = meas(graph, binary)
    return metrics


def analysis_and_vis(image_or_path) -> tuple[dict[str, float], np.ndarray]:
    image = read(image_or_path)
    binary = seg(image)
    skeleton = skel(binary)
    trunks = trunk(image, skeleton)
    graph = grfy(image, skeleton, trunks)
    metrics = meas(graph, binary)
    image_vis = vis_ACCM(graph, image)
    return metrics, image_vis





def read(image_or_path, **kwargs) -> np.ndarray:
    return read_image(image_or_path, **kwargs)


def seg(image: np.ndarray) -> np.ndarray:
    if not image.shape == (384, 384):
        raise TypeError('This method is expected to input a grayscale image with a size of 384*384.')
    return segmenter(image)


def skel(binary: np.ndarray, **kwargs) -> np.ndarray:
    if not np.isin(binary, [0, 255]).all():
        raise ValueError('This method is expected to receive binary images composed solely of 0s and 255s as input.')
    return get_skeleton(binary, **kwargs)


def trunk(image: np.ndarray, skeleton: np.ndarray, **kwargs) -> np.ndarray:
    return extract_trunk(image, skeleton, **kwargs)


def grfy(image: np.ndarray, skeleton_image: np.ndarray, trunk_image: np.ndarray | None = None):
    return graphify(image, skeleton_image, trunk_image)


def meas(graph: nx.MultiGraph, binary_image: np.ndarray, decimal=3) -> dict[str, float]:
    return get_metrics(graph, binary_image, decimal)


def hist_std(image: np.ndarray) -> np.ndarray:
    return histogram_standardization(image)


def vgnt_corr(image: np.ndarray) -> np.ndarray:
    return vignetting_correction(image)


def est_wid(image: np.ndarray, skeleton_image: np.ndarray) -> np.ndarray:
    return estimate_width(image, skeleton_image)
