import networkx as nx

from superccm.impl.graph.trunk import get_trunk_groups
from superccm.impl.utils.prune import prune
from superccm.impl.graph.utils import is_near_edge, SHAPE

MIN_LENGTH_THRESH = 250


def graphify_postprocess(graph: nx.MultiGraph) -> nx.MultiGraph:
    groups = get_trunk_groups(graph)
    for group in groups:
        nodes, edges, node_objs, edge_objs = (
            group['nodes'], group['edges'],
            group['node_objs'], group['edge_objs']
        )
        length_edges = sum(obj.length for obj in edge_objs)
        length_nodes = sum(obj.length for obj in node_objs)

        # 长度不足
        if (length_edges + length_nodes) < MIN_LENGTH_THRESH:
            for edge_obj in edge_objs:
                edge_obj.is_trunk = False

        # 端点均不在图像边缘
        if all(not is_near_edge(*obj.centroid, SHAPE, 38)
               for obj in node_objs
               if obj.type == 'End'):
            for edge_obj in edge_objs:
                edge_obj.is_trunk = False

    return graph
