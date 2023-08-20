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
    return list(res)


if __name__ == "__main__":
    g = Graph()
    g.add_edge(0, 1)
    g.add_edge(2, 1)
    g.add_edge(3, 1)
    g.add_edge(1, 4)
    g.add_edge(1, 5)
    g.add_edge(4, 6)
    g.add_edge(6, 7)
    g.add_edge(5, 7)
    sorted_vertices = kahn_algorithm(g)
    print(sorted_vertices)
