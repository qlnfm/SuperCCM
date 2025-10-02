import networkx as nx
import numpy as np
import cv2

from ..topology.graph import NerveGraph
from ..topology.morphology import NerveImage
from ..common import get_canvas
from .bfs import find_shortest_path
from .tc import get_tc
from .fracdim import fractal_dimension

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


class MainNerveSkeleton:
    def __init__(self, edges, nodes, end_nodes):
        self.edges = edges.copy()
        self.nodes = nodes.copy()
        self.end_nodes = end_nodes

        self.bone = None
        self.body = None
        self.process()

    def process(self):
        canvas = get_canvas()
        for edge in self.edges:
            canvas[edge.bone > 0] = 255
        for node in self.nodes:
            canvas[node.bone > 0] = 255

        coords = find_shortest_path(canvas, *tuple(tuple(int(x) for x in n.centroid) for n in self.end_nodes))
        canvas = get_canvas()
        for x, y in coords:
            canvas[y, x] = 255

        self.bone = canvas


def get_main_nerves(n_image: NerveImage, n_graph: NerveGraph) -> list[MainNerveSkeleton]:
    """ Generate the main nerve fiber objects """
    G = n_graph.graph.copy()

    edges_to_remove = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if d['obj'].edge_type != 'main'
    ]
    G.remove_edges_from(edges_to_remove)
    isolated_nodes = list(nx.isolates(G))
    G.remove_nodes_from(isolated_nodes)

    connected_subgraphs = [
        G.subgraph(c).copy()
        for c in nx.connected_components(nx.Graph(G))
    ]

    main_nerves = []
    for subgraph in connected_subgraphs:
        nodes = [data['obj'] for _, data in subgraph.nodes(data=True)]
        edges = [data['obj'] for _, _, _, data in subgraph.edges(keys=True, data=True)]
        end_nodes = [data['obj']
                     for n, data in subgraph.nodes(data=True)
                     if len([i for i in subgraph.neighbors(n) if i != n]) == 1]
        main_nerve = MainNerveSkeleton(edges, nodes, end_nodes)
        main_nerves.append(main_nerve)

    return main_nerves


def get_primary_branch_count(n_image: NerveImage, n_graph: NerveGraph):
    """ Get the count of the primary nerve fiber branches """
    G = n_graph.graph.copy()

    result = set()

    for node in G.nodes:
        edges = G.edges(node, keys=True, data=True)
        main_count = len(tuple((u, v, k) for u, v, k, d in edges if d['obj'].edge_type == 'main'))

        if main_count == 2:
            for u, v, k, d in edges:
                u, v = max(u, v), min(u, v)
                if d['obj'].edge_type != 'main':
                    result.add((u, v, k))

    primary_branch_count = len(result)
    return primary_branch_count


def get_total_length(n_image: NerveImage, n_graph: NerveGraph):
    """ Get the total length of all nerve fibers """
    total_length = 0
    for edge in n_image.edges.values():
        total_length += edge.length
    for node in n_image.nodes.values():
        total_length += node.length
    return total_length


def get_total_area(n_image: NerveImage, n_graph: NerveGraph):
    """ Get the total area of all nerve fibers """
    total_area = cv2.countNonZero(n_image.binary)
    return total_area


def get_branch_node_count(n_image: NerveImage, n_graph: NerveGraph):
    """ Get the count of all branch points """
    branch_node_count = len(tuple(n for n in n_graph.graph.nodes if n_graph.graph.degree(n) >= 3))
    return branch_node_count


def get_tortuosity_coefficient(main_nerves: Sequence[MainNerveSkeleton]):
    """ Get the average curvature coefficients of all major nerves """
    total_tc = sum(get_tc(mn.bone) for mn in main_nerves)
    return total_tc / len(main_nerves)


def get_fractal_dimension(n_image: NerveImage, n_graph: NerveGraph):
    """ Get the fractal dimension """
    fracdim = fractal_dimension(n_image.binary)
    return fracdim


def get_metrics(n_graph: NerveGraph, digit=3) -> dict[str, float]:
    n_image = n_graph.nerve_image
    main_nerves = get_main_nerves(n_image, n_graph)
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

    # CNFL
    x = get_total_length(n_image, n_graph)
    length = x * length_per_pix
    CNFL = np.round(length / view_area, digit)
    metrics['CNFL'] = CNFL

    # CNFD
    x = len(main_nerves)
    CNFD = np.round(x / view_area, digit)
    metrics['CNFD'] = CNFD

    # CNBD
    x = get_primary_branch_count(n_image, n_graph)
    CNBD = np.round(x / view_area, digit)
    metrics['CNBD'] = CNBD

    # CNFA
    x = get_total_area(n_image, n_graph)
    area = x * area_per_pix
    CNFA = np.round(area / view_area, digit)
    metrics['CNFA'] = CNFA

    # CNFW
    area = get_total_area(n_image, n_graph) * area_per_pix
    length = get_total_length(n_image, n_graph) * length_per_pix
    width = area / length
    CNFW = np.round(width / view_area, digit)
    metrics['CNFW'] = CNFW

    # CTBD
    x = get_branch_node_count(n_image, n_graph)
    CTBD = np.round(x / view_area, digit)
    metrics['CTBD'] = CTBD

    # CNFrD
    x = get_fractal_dimension(n_image, n_graph)
    CFracDim = np.round(x, digit)
    metrics['CNFrD'] = CFracDim

    # CNFT
    x = get_tortuosity_coefficient(main_nerves) if len(main_nerves) else 0
    TC = np.round(x, digit)
    metrics['CNFT'] = TC

    return metrics






