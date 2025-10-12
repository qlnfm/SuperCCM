import networkx as nx

from superccm.impl.utils.tools import get_canvas
from superccm.impl.utils.prune import prune


def get_trunk_objs(graph: nx.MultiGraph):
    """
    :return:
      {
          "node_objs": [obj1, obj2, ...],  # 对应节点的 obj（如果有）
          "edge_objs": [obj1, obj2, ...],  # 对应边的 obj
      }
    """
    # 1. 找出 trunk 边
    trunk_edges = [
        (u, v, k)
        for u, v, k, d in graph.edges(keys=True, data=True)
        if hasattr(d.get("obj", None), "is_trunk") and d["obj"].is_trunk
    ]

    # 2. 构建 trunk 子图
    trunk_subgraph = graph.edge_subgraph(trunk_edges).copy()

    # 3. 找出连通分量
    components = nx.connected_components(trunk_subgraph)

    # 4. 收集每个分量的节点、边及 obj
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


def extract_trunk_canvas(graph: nx.MultiGraph):
    canvas = get_canvas(1)
    for group in get_trunk_objs(graph):
        node_objs, edge_objs = group['node_objs'], group['edge_objs']
        for node_obj in node_objs:
            canvas = canvas + node_obj.canvas
        for edge_obj in edge_objs:
            canvas = canvas + edge_obj.canvas

    canvas = prune(canvas)
    return canvas



