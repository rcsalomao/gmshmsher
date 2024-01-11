from collections import deque
from copy import deepcopy

from .smol_graph import Graph


def kahn_algorithm(graph: Graph):
    g = deepcopy(graph)
    res = deque()
    while g.num_verts:
        vertex_to_remove = deque()
        for u, value in g.inv_adj_list.items():
            if not value:
                vertex_to_remove.append(u)
                res.append(u)
        for u in vertex_to_remove:
            g.del_vertex(u)
    return res
