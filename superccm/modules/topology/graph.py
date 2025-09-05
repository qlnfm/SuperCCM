import math
import cv2
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Set, Literal
from collections import Counter

from .morphology import NerveImage
from .component import SkeletonComponent

# Image shape
SHAPE = (384, 384)
INITIAL_EDGE_LENGTH_THRESHOLD = 25
INITIAL_EDGE_LENGTH_GRADIENT = 5
SHORT_EDGE_LENGTH_THRESHOLD = 1
EDGES_ANGLE_THRESHOLD = 60.0
# The minimum length of the main nerve fibers
MIN_MAIN_NERVE_LENGTH = 300
# The minimum width of the main nerve fibers
MIN_MAIN_NERVE_WIDTH = 6000
# The minimum length of the branches emanating from the main nerve fibers
MIN_PRIMARY_BRANCH_LENGTH = 3

MultiGraph = nx.MultiGraph
Edge = Tuple[int, int, int]  # (u, v, key)
Path = List[Edge]


class NerveGraph:
    def __init__(self, nerve_image: NerveImage):
        self.nerve_image = nerve_image
        self.binary_ratio = cv2.countNonZero(nerve_image.binary) / SHAPE[0] / SHAPE[1]
        self.graph = nx.MultiGraph()

        self.process()
        self.assign_node_type()
        self.assign_edge_type()

        self.filter_short_end_edge()
        self.assign_node_type()

    def process(self):
        for idx, node in self.nerve_image.nodes.items():
            self.graph.add_node(
                idx,
                obj=node,
                centroid=node.centroid,
            )

        for _, edge in self.nerve_image.edges.items():
            self.graph.add_edge(
                *edge.neighbors,
                obj=edge,
                width=np.mean(edge.weights) / 64,
                length=edge.length,
            )

    def assign_node_type(self):
        for node in self.graph.nodes():
            # edge_num = self.graph.degree(node)
            edge_num = len([i for i in self.graph.neighbors(node) if i != node])
            if edge_num == 1:
                self.graph.nodes[node]['obj'].node_type = 'end'
            elif edge_num >= 3:
                self.graph.nodes[node]['obj'].node_type = 'branch'
            else:
                self.graph.nodes[node]['obj'].node_type = 'other'
                if any(d['obj'].edge_type == 'main' for _, _, _, d in self.graph.edges(node, keys=True, data=True)):
                    self.graph.nodes[node]['obj'].color = (0, 0, 255)
                else:
                    self.graph.nodes[node]['obj'].color = (255, 0, 0)

    def assign_edge_type(self):
        width_ratio = self.binary_ratio
        assign_edge_types(self.graph, width_ratio)

    def filter_short_end_edge(self):
        edges_to_remove = []
        edges_to_remove_image = []
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if data['obj'].length < MIN_PRIMARY_BRANCH_LENGTH and any(
                    self.graph.nodes[x]['obj'].node_type == 'end' for x in (u, v)):
                edges_to_remove.append((u, v, key))
                edges_to_remove_image.append(data['obj'].index)
        self.graph.remove_edges_from(edges_to_remove)
        for edge in edges_to_remove_image:
            del self.nerve_image.edges[edge]

        # Remove all isolated nodes (nodes without connections)
        isolated_nodes = list(nx.isolates(self.graph))
        self.graph.remove_nodes_from(isolated_nodes)
        for node in isolated_nodes:
            del self.nerve_image.nodes[node]


def get_edge_vector(graph: MultiGraph, edge: Edge, from_node: int) -> Tuple[float, float]:
    """ Calculate the vector of an edge that points from from_node to another node of the edge. """
    u, v, _ = edge
    if from_node not in (u, v):
        raise ValueError(f"Node {from_node} dose not belong to Edge {edge}.")

    start_pos = graph.nodes[from_node]['obj'].centroid
    end_node = v if u == from_node else u
    end_pos = graph.nodes[end_node]['obj'].centroid

    return end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]


def calculate_vector_angle(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """ Calculate the Angle between two vectors using the dot product (unit: degrees). """
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude1 = math.hypot(*v1)
    magnitude2 = math.hypot(*v2)

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    cos_arg = max(-1.0, min(1.0, dot_product / (magnitude1 * magnitude2)))
    return math.degrees(math.acos(cos_arg))


def find_initial_edge(subgraph: MultiGraph) -> Optional[Edge]:
    """
    Find an initial edge in the subgraph to start the identification of the main trunk.
    Start the search from length > INITIAL_EDGE_LENGTH_THRESHOLD.
    If not, reduce the threshold with INITIAL_EDGE_LENGTH_GRADIENT as the step size.
    Among the edges that meet the conditions, select the one with the largest width.
    """
    length_threshold = INITIAL_EDGE_LENGTH_THRESHOLD
    while length_threshold >= 0:
        candidate_edges = [
            (u, v, k) for u, v, k, data in subgraph.edges(data=True, keys=True)
            if u != v and data['obj'].edge_type is None and data['obj'].length > length_threshold
        ]
        if candidate_edges:
            return max(candidate_edges, key=lambda e: subgraph.edges[e]['obj'].width)
        length_threshold -= INITIAL_EDGE_LENGTH_GRADIENT
    return None


def find_next_candidate_paths(graph: MultiGraph, start_node: int) -> List[Path]:
    """
    Starting from a starting node, all possible extension paths are sought through depth-first search (DFS).
    A path can traverse a series of unprocessed "short edges" (length < SHORT_EDGE_LENGTH_THRESHOLD).
    It terminates when encountering a "long edge" (length >= SHORT_EDGE_LENGTH_THRESHOLD) or a path endpoint.
    """
    candidate_paths: List[Path] = []
    # DFS stack, storing tuples (current node, current path, and the set of nodes visited in the path)
    stack: List[Tuple[int, Path, Set[int]]] = []

    # Initialization stack
    for u, v, k, data in graph.edges(start_node, data=True, keys=True):
        if data['obj'].edge_type is None:
            edge = (u, v, k)
            neighbor = v if u == start_node else u
            stack.append((neighbor, [edge], {start_node, neighbor}))

    while stack:
        current_node, path, visited_nodes = stack.pop()
        last_edge_data = graph.edges[path[-1]]['obj']

        # If the last edge of a path is a long edge, then this path constitutes a candidate and terminates here
        if last_edge_data.length >= SHORT_EDGE_LENGTH_THRESHOLD:
            candidate_paths.append(path)
            continue

        # Look for the next edge that can be extended
        next_moves = []
        for u_next, v_next, k_next, data_next in graph.edges(current_node, data=True, keys=True):
            neighbor = v_next if u_next == current_node else u_next
            if neighbor not in visited_nodes and data_next['obj'].edge_type is None:
                next_moves.append((u_next, v_next, k_next))

        # If there is no next step (i.e., reaching the endpoint), then this path also constitutes a candidate
        if not next_moves:
            candidate_paths.append(path)
        else:
            # ...Otherwise, add the new extended path to the stack and continue the search
            for next_edge in next_moves:
                neighbor = next_edge[1] if next_edge[0] == current_node else next_edge[0]
                stack.append((neighbor, path + [next_edge], visited_nodes | {neighbor}))

    return candidate_paths


def extend_trunk_from_node(graph: MultiGraph, start_node: int, first_main_edge: Edge) -> List[Edge]:
    """
    Starting from a given node and the initial backbone edge, heuristically extend the backbone.
    """
    # Defensive check: If the initial edge is a self-loop, return directly without extension
    if first_main_edge[0] == first_main_edge[1]:
        return []

    newly_main_edges: List[Edge] = []
    current_main_edge = first_main_edge
    current_node = start_node

    while True:
        possible_prev_nodes = [n for n in current_main_edge[:2] if n != current_node]
        if not possible_prev_nodes:
            break
        prev_node = possible_prev_nodes[0]

        vec_main = get_edge_vector(graph, current_main_edge, from_node=prev_node)

        candidate_paths = find_next_candidate_paths(graph, current_node)
        if not candidate_paths:
            break

        best_path, min_width_diff = None, float('inf')

        for path in candidate_paths:
            first_edge_in_path = path[0]
            vec_candidate = get_edge_vector(graph, first_edge_in_path, from_node=current_node)
            angle = calculate_vector_angle(vec_main, vec_candidate)

            if angle <= EDGES_ANGLE_THRESHOLD:
                terminal_edge = path[-1]
                width_diff = abs(graph.edges[current_main_edge]['obj'].width - graph.edges[terminal_edge]['obj'].width)
                if width_diff < min_width_diff:
                    min_width_diff, best_path = width_diff, path

        if best_path:
            for edge in best_path:
                if graph.edges[edge]['obj'].edge_type is None:
                    graph.edges[edge]['obj'].edge_type = 'main'
                    newly_main_edges.append(edge)

            for path in candidate_paths:
                if path != best_path:
                    for edge in path:
                        if graph.edges[edge]['obj'].edge_type is None:
                            graph.edges[edge]['obj'].edge_type = 'side'

            current_main_edge = best_path[-1]

            if len(best_path) > 1:
                p_node_set = set(best_path[-2][:2]) & set(best_path[-1][:2])
                if not p_node_set:
                    break
                p_node = p_node_set.pop()
            else:
                p_node = current_node

            node_a, node_b = current_main_edge[:2]
            if node_a == node_b:
                break
            current_node = node_b if node_a == p_node else node_a
        else:
            for path in candidate_paths:
                for edge in path:
                    graph.edges[edge]['obj'].edge_type = 'side'
            break

    return newly_main_edges


def process_subgraph(subgraph: MultiGraph, width_ratio):
    """ Apply a complete backbone/branch determination algorithm to a single connected subgraph. """

    def find_endpoints(edges):
        node_counts = Counter()
        for u, v, _ in edges:
            node_counts[u] += 1
            node_counts[v] += 1

        endpoints = [node for node, count in node_counts.items() if count == 1]
        return endpoints

    while True:
        initial_edge = find_initial_edge(subgraph)
        if not initial_edge:
            break

        subgraph.edges[initial_edge]['obj'].edge_type = 'main'
        current_trunk_edges = [initial_edge]

        node1, node2, _ = initial_edge

        trunk_from_node1 = extend_trunk_from_node(subgraph, node1, initial_edge)
        trunk_from_node2 = extend_trunk_from_node(subgraph, node2, initial_edge)
        current_trunk_edges.extend(trunk_from_node1)
        current_trunk_edges.extend(trunk_from_node2)

        total_length = sum(subgraph.edges[edge]['obj'].length for edge in current_trunk_edges)
        average_width = sum(subgraph.edges[edge]['obj'].length * subgraph.edges[edge]['obj'].width for edge in
                            current_trunk_edges) / total_length
        if ((total_length < MIN_MAIN_NERVE_LENGTH) or (average_width < MIN_MAIN_NERVE_WIDTH * (width_ratio ** 2))
                or any(subgraph.degree(n) > 1 for n in find_endpoints(current_trunk_edges))):
            for edge in current_trunk_edges:
                subgraph.edges[edge]['obj'].edge_type = 'side'


def assign_edge_types(graph: MultiGraph, width_ratio) -> None:
    """
    The main function that performs the backbone/branch determination algorithm on the entire graph.
    This function will handle all possible disconnected subgraphs in the graph.
    """
    # Make sure that the types of all edges are reset so that they can be run repeatedly
    for u, v, k, data in graph.edges(data=True, keys=True):
        if 'obj' in data and isinstance(data['obj'], SkeletonComponent):
            data['obj'].edge_type = None

    # Decompose the graph into multiple connected subgraphs and process each subgraph independently
    # Use.copy() to ensure that modifications to the subgraph do not affect the iteration process
    connected_components_nodes = [c for c in nx.connected_components(graph)]

    for node_set in connected_components_nodes:
        subgraph = graph.subgraph(node_set).copy()
        process_subgraph(subgraph, width_ratio)

        # Synchronize the processing result from the subgraph back to the original graph
        for u, v, k, data in subgraph.edges(data=True, keys=True):
            graph.edges[u, v, k]['obj'].edge_type = data['obj'].edge_type
