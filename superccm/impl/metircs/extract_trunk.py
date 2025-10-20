import networkx as nx

from superccm.impl.utils.tools import get_canvas
from superccm.impl.utils.prune import prune


def get_trunk_objs(graph: nx.MultiGraph):
    """
    :return:
      {
          "node_objs": [obj1, obj2, ...],
          "edge_objs": [obj1, obj2, ...],
      }
    """
    trunk_edges = [
        (u, v, k)
        for u, v, k, d in graph.edges(keys=True, data=True)
        if hasattr(d.get("obj", None), "is_trunk") and d["obj"].is_trunk
    ]

    trunk_subgraph = graph.edge_subgraph(trunk_edges).copy()

    components = nx.connected_components(trunk_subgraph)

    groups = []
    for nodes in components:
        sub = trunk_subgraph.subgraph(nodes)
        edges = list(sub.edges(keys=True))

        group = {
            "node_objs": [graph.nodes[n].get("obj") for n in nodes if "obj" in graph.nodes[n]],
            "edge_objs": [
                graph[u][v][k]["obj"]
                for u, v, k in edges
                if "obj" in graph[u][v][k]
            ],
        }
        groups.append(group)

    return groups


