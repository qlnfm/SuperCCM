from superccm.impl.segment import segment
from superccm.impl.skeleton.skeletonize import get_skeleton
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
    graph = grfy(image, skeleton)
    metrics = meas(graph, binary)
    return metrics


def analysis_and_vis(image_or_path) -> tuple[dict[str, float], np.ndarray]:
    image = read(image_or_path)
    binary = seg(image)
    skeleton = skel(binary)
    graph = grfy(image, skeleton)
    metrics = meas(graph, binary)
    image_vis = vis_ACCM(graph, image)
    return metrics, image_vis


def save_image(image, path='result.png'):
    """ 保存一张图片 """
    extend = '.' + path.split('.')[-1]
    retval, buffer = cv2.imencode(extend, image.astype('uint8'))
    with open(path, 'wb') as f:
        f.write(buffer)


def show_image(image):
    """ 展示一张图片 """
    image_show = image.copy().astype('uint8')
    if np.amax(image_show) == 1:
        image_show = image_show * 255
    cv2.imshow('Show', image_show)
    cv2.waitKey(0)


def read(image_or_path) -> np.ndarray:
    return read_image(image_or_path)


def seg(image: np.ndarray, *, post_process=True) -> np.ndarray:
    if not image.shape == (384, 384):
        raise TypeError('This method is expected to input a grayscale image with a size of 384*384.')
    return segmenter(image, post_process=post_process)


def skel(image: np.ndarray) -> np.ndarray:
    if not np.isin(image, [0, 255]).all():
        raise ValueError('This method is expected to receive binary images composed solely of 0s and 255s as input.')
    return get_skeleton(image)


def grfy(image: np.ndarray, skeleton_image: np.ndarray):
    return graphify(image, skeleton_image)


def meas(graph: nx.MultiGraph, binary_image: np.ndarray, decimal=3) -> dict[str, float]:
    return get_metrics(graph, binary_image, decimal)


def hist_std(image: np.ndarray) -> np.ndarray:
    return histogram_standardization(image)


def vgnt_corr(image: np.ndarray) -> np.ndarray:
    return vignetting_correction(image)


def est_wid(image: np.ndarray, skeleton_image: np.ndarray) -> np.ndarray:
    return estimate_width(image, skeleton_image)
