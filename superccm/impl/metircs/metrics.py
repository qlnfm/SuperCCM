import networkx as nx
import numpy as np
import cv2

from superccm.impl.utils.tools import get_canvas, get_split_label
from superccm.impl.metircs.tc import get_tc
from superccm.impl.metircs.fracdim import fractal_dimension
from superccm.impl.metircs.extract_trunk import get_trunk_objs, extract_trunk_canvas
from superccm.impl.metircs.utils import check_connectivity, graph_to_skeleton
from superccm.impl.metircs.reconstruction_binary import reconstruct_binary

from typing import Literal, Sequence

METRICS = Literal[
    'CNFL',
    'CNFD',
    'CNBD',
    'CNFA',
    'CNFW',
    'CTBD',
    'CNFT',
    'CNFrD'
]

# Image shape
SHAPE = (384, 384)
# Field of view range (mm)
VIEW_DIAMETER_MM = 0.4
view_area = VIEW_DIAMETER_MM ** 2  # mm2
length_per_pix = VIEW_DIAMETER_MM / SHAPE[0]  # mm_per_pix
area_per_pix = (VIEW_DIAMETER_MM ** 2) / (SHAPE[0] * SHAPE[1])  # mm2_per_pix


def cal_total_length(graph: nx.MultiGraph) -> float:
    """ 总长度 = edge总长度 + node总长度 + node与edge连接处长度 """
    total_length = 0
    for u, v, k, data in graph.edges(keys=True, data=True):
        obj = data['obj']
        total_length += obj.length

    for idx, data in graph.nodes(data=True):
        node_obj = data['obj']
        total_length += node_obj.length

        edges = graph.edges(idx, keys=True, data=True)
        for u, v, k, d in edges:
            edge_obj = d['obj']
            connectivity = check_connectivity(node_obj.canvas, edge_obj.canvas)
            if connectivity == '8-connected':
                total_length += 1
            elif connectivity == '4-connected':
                total_length += np.sqrt(2)

    return total_length


def get_metrics(graph: nx.MultiGraph, binary_image: np.ndarray, decimal=3) -> dict[str, float]:
    metrics = {
        'CNFL': None,  # mm/mm2
        'CNFD': None,  # n/mm2
        'CNBD': None,  # n/mm2
        'CNFA': None,  # mm2/mm2
        'CNFW': None,  # mm/mm2
        'CTBD': None,  # n/mm2
        'CNFT': None,
        'CNFrD': None,
    }
    total_length = cal_total_length(graph)
    trunks = get_trunk_objs(graph)
    skeleton = graph_to_skeleton(graph)
    binary = reconstruct_binary(binary_image, skeleton)
    # CNFL
    length = total_length * length_per_pix
    CNFL = np.round(length / view_area, decimal)
    metrics['CNFL'] = CNFL

    # CNFD
    x = len(trunks)
    CNFD = np.round(x / view_area, decimal)
    metrics['CNFD'] = CNFD

    # CNBD
    x = sum([n.type == 'Branch' for trunk in trunks for n in trunk['node_objs']])
    CNBD = np.round(x / view_area, decimal)
    metrics['CNBD'] = CNBD

    # CNFA
    x = cv2.countNonZero(binary)
    area = x * area_per_pix
    CNFA = np.round(area / view_area, decimal)
    metrics['CNFA'] = CNFA

    # CNFW
    width = area / length
    CNFW = np.round(width / view_area, decimal)
    metrics['CNFW'] = CNFW

    # CTBD
    x = sum([data['obj'].type == 'Branch' for _, data in graph.nodes(data=True)])
    CTBD = np.round(x / view_area, decimal)
    metrics['CTBD'] = CTBD

    # CNFrD
    x = fractal_dimension(binary)
    CFracDim = np.round(x, decimal)
    metrics['CNFrD'] = CFracDim

    # CNFT
    trunk_canvas = extract_trunk_canvas(graph)
    trunk_labels = get_split_label(trunk_canvas)
    if len(trunk_labels):
        x = sum(get_tc(label) for label in trunk_labels) / len(trunk_labels)
    else:
        x = None
    TC = np.round(x, decimal)
    metrics['CNFT'] = TC

    return metrics
