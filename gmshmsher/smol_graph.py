from pprint import pp


class Graph(object):
    def __init__(self):
        self.adj_list = {}
        self.inv_adj_list = {}
        self.num_verts = 0

    def __contains__(self, key):
        return key in self.adj_list

    def __iter__(self):
        return iter(self.adj_list)

    def add_vertex(self, key):
        self.adj_list[key] = {}
        self.inv_adj_list[key] = set()
        self.num_verts += 1

    def del_vertex(self, key):
        i = self.get_vertex_edges(key)
        if i is not None:
            for u in self.inv_adj_list.get(key):
                del self.adj_list[u][key]
            for v in self.adj_list[key].keys():
                self.inv_adj_list[v].remove(key)
            del self.adj_list[key]
            del self.inv_adj_list[key]
            self.num_verts -= 1
        else:
            return i

    def get_vertex_edges(self, key):
        return self.adj_list.get(key)

    def get_vertices(self):
        return self.adj_list.keys()

    def add_edge(self, u, v, weight=0):
        if u not in self.adj_list:
            self.add_vertex(u)
        if v not in self.adj_list:
            self.add_vertex(v)
        self.adj_list[u][v] = weight
        self.inv_adj_list[v].add(u)

    def del_edge(self, u, v):
        i = self.get_vertex_edges(u)
        if i is not None:
            j = i.get(v)
            if j:
                del i[v]
                self.inv_adj_list[v].remove(u)
            else:
                return j
        else:
            return i

    def get_weight(self, u, v):
        i = self.get_vertex_edges(u)
        if i is not None:
            return i.get(v)
        else:
            return i

    def get_edges(self):
        pass


if __name__ == "__main__":
    g = Graph()
    g.add_edge(0, 1, 3)
    g.add_edge(0, 2, 4)
    g.add_edge(1, 3, 5)
    g.add_edge(2, 3, 6)
    pp(g.adj_list)
    pp(g.inv_adj_list)
    print(g.get_weight(2, 3))
    print(g.get_vertices())
    pp(g.get_vertex_edges(2))
    # g.del_edge(1, 3)
    # g.del_edge(2, 3)
    g.del_vertex(1)
    pp(g.adj_list)
    pp(g.inv_adj_list)
