from superccm.impl.segment.segment import get_binary
from superccm.impl.skeleton.skeletonize import get_skeleton
from superccm.impl.trunk.extract_trunks import extract_trunks
from superccm.impl.graph.graphify import graphify
from superccm.impl.graph.vis import vis_ACCM
from superccm.impl.metircs.metrics import get_metrics
from superccm.impl.io.read import read_image
from superccm.impl.utils.histogram_matching import histogram_standardization
from superccm.impl.utils.ccm_vignetting import vignetting_correction
from superccm.impl.utils.estimate_width import estimate_width

import numpy as np
import networkx as nx


def analysis(image_or_path, um_pixel_ratio=400/384) -> dict[str, float]:
    image, mask, area = read(image_or_path)
    binary = seg(image)
    skeleton = skel(binary, mask, um_pixel_ratio)
    graph = grfy(image, skeleton)
    graph, trunks = trunk(graph, mask)
    metrics = meas(graph, binary, trunks, area, um_pixel_ratio)
    return metrics


def analysis_and_vis(image_or_path, um_pixel_ratio=400/384) -> tuple[dict[str, float], np.ndarray]:
    image, mask, area = read(image_or_path)
    binary = seg(image)
    skeleton = skel(binary, mask, um_pixel_ratio)
    graph = grfy(image, skeleton)
    graph, trunks = trunk(graph, mask)
    metrics = meas(graph, binary, trunks, area, um_pixel_ratio)
    image_vis = vis_ACCM(graph, image.shape[:2], image)
    return metrics, image_vis


def read(image_or_path) -> tuple[np.ndarray, np.ndarray, int]:
    return read_image(image_or_path)


def seg(image: np.ndarray) -> np.ndarray:
    return get_binary(image)


def skel(binary: np.ndarray, mask: np.ndarray, um_pixel_ratio: float) -> np.ndarray:
    if not np.isin(binary, [0, 255]).all():
        raise ValueError('This method is expected to receive binary images composed solely of 0s and 255s as input.')
    return get_skeleton(binary, mask, um_pixel_ratio)


def trunk(graph: nx.MultiGraph, mask: np.ndarray) -> tuple[nx.MultiGraph, np.ndarray]:
    return extract_trunks(graph, mask)


def grfy(image: np.ndarray, skeleton_image: np.ndarray):
    return graphify(image, skeleton_image)


def meas(
        graph: nx.MultiGraph, binary_image: np.ndarray, trunk_image: np.ndarray,
        area, um_pixel_ratio, decimal=3
) -> dict[str, float]:
    return get_metrics(graph, binary_image, trunk_image, area, um_pixel_ratio, decimal)


def hist_std(image: np.ndarray) -> np.ndarray:
    return histogram_standardization(image)


def vgnt_corr(image: np.ndarray) -> np.ndarray:
    return vignetting_correction(image)


def est_wid(image: np.ndarray, skeleton_image: np.ndarray) -> np.ndarray:
    return estimate_width(image, skeleton_image)
