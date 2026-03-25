import networkx as nx
import numpy as np
import cv2

from superccm.impl.utils.tools import get_split_label
from superccm.impl.metircs.tc import get_tc
from superccm.impl.metircs.fracdim import fractal_dimension
from superccm.impl.metircs.extract_trunk import get_trunk_objs
from superccm.impl.metircs.utils import check_connectivity, graph_to_skeleton
from superccm.impl.metircs.reconstruction_binary import reconstruct_binary


def cal_total_length(graph: nx.MultiGraph) -> float:
    """
    Total length =
    total length of edges +
    total length of nodes +
    length at the connection points between nodes and edges
    """
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


def get_metrics(
        graph: nx.MultiGraph,
        binary_image: np.ndarray,
        trunk_image: np.ndarray,
        area: int,
        um_pixel_ratio,
        decimal=3
) -> dict[str, float]:
    metrics = {
        'Resolution (μm/pixel)': None,
        'Image Area (pixel)': None,
        'Image Area (mm2)': None,
        'Length of Nerves (pixel)': None,
        'Length of Nerves (mm)': None,
        'CNFL (mm/mm2)': None,
        'Count of Main Nerves (n)': None,
        'CNFD (n/mm2)': None,
        'Count of Primary Branches (n)': None,
        'Count of Primary Branch Points (n)': None,
        'CNBD (n/mm2)': None,
        'Nerve Area (pixel)': None,
        'Nerve Area (mm2)': None,
        'CNFA (mm2/mm2)': None,
        'Count of Branch Points (n)': None,
        'CTBD (n/mm2)': None,
        'CNFT': None,
        'CNFrD': None,
    }

    metrics['Resolution (μm/pixel)'] = um_pixel_ratio
    n = um_pixel_ratio / 1000  # mm/pixel

    metrics['Image Area (pixel)'] = area
    area_mm2 = area * n * n
    metrics['Image Area (mm2)'] = area_mm2

    total_length = cal_total_length(graph)
    metrics['Length of Nerves (pixel)'] = total_length
    length_mm = total_length * n
    metrics['Length of Nerves (mm)'] = length_mm
    metrics['CNFL (mm/mm2)'] = length_mm / area_mm2

    trunks = get_trunk_objs(graph)
    skeleton = graph_to_skeleton(graph, binary_image.shape)
    binary = reconstruct_binary(binary_image, skeleton)

    cnt_main = len(trunks)
    metrics['Count of Main Nerves (n)'] = cnt_main
    metrics['CNFD (n/mm2)'] = cnt_main / area_mm2

    cnt_pb = None
    cnt_pbp = sum([n.type == 'Branch' for trunk in trunks for n in trunk['node_objs']])
    metrics['Count of Primary Branches (n)'] = cnt_pb
    metrics['Count of Primary Branch Points (n)'] = cnt_pbp
    metrics['CNBD (n/mm2)'] = cnt_pbp / area_mm2

    area_nerve = cv2.countNonZero(binary)
    area_nerve_mm2 = area_nerve * n * n
    metrics['Nerve Area (pixel)'] = area_nerve
    metrics['Nerve Area (mm2)'] = area_nerve_mm2
    metrics['CNFA (mm2/mm2)'] = area_nerve_mm2 / area_mm2

    # CTBD
    cnt_bp = sum([data['obj'].type == 'Branch' for _, data in graph.nodes(data=True)])
    metrics['Count of Branch Points (n)'] = cnt_bp
    metrics['CTBD (n/mm2)'] = cnt_bp / area_mm2

    # CNFrD
    CFracDim = fractal_dimension(binary)
    metrics['CNFrD'] = CFracDim

    # CNFT
    trunk_canvas = trunk_image
    trunk_labels = get_split_label(trunk_canvas)
    if len(trunk_labels):
        x = sum(get_tc(label) for label in trunk_labels) / len(trunk_labels)
    else:
        x = None
    metrics['CNFT'] = x

    metrics = {
        k: np.round(v, decimals=decimal) if v else v
        for k, v in metrics.items()
    }

    return metrics
