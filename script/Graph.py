class Graph:
    def __init__(self, vertices, edges):

        self.vert_dict = {}
        self.edge_dict = {}
        self.num_vertices = 0
        self.num_edges = 0

        for vtx in vertices:
            self.add_vertex(vtx)
        for edge in edges:
            self.add_edge(edge)

        # generate derived attr
        for vtx in vertices:
            vtx.gen_derived_attr()

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        self.vert_dict[node.get_id()] = node
        return node 

    def get_vertex(self, vid):
        if vid in self.vert_dict:
            return self.vert_dict[vid]
        else:
            return None

    def add_edge(self, edge):
        self.num_edges = self.num_edges + 1
        self.edge_dict[edge.get_id()] = edge

        # add neighbors
        frm = edge.get_left_node_id()
        to = edge.get_right_node_id()
        if edge.get_directed():
            # directed graph add neighbors
            self.vert_dict[frm].add_neighbor(edge)
            self.vert_dict[frm].incOutgoing()
            self.vert_dict[to].incIncoming()
        else:
            # undirected graph add neighbors
            self.vert_dict[frm].add_neighbor(edge)
            self.vert_dict[to].add_neighbor(edge)
            self.vert_dict[frm].incOutgoing()
            self.vert_dict[to].incOutgoing()
            self.vert_dict[to].incIncoming()
            self.vert_dict[frm].incIncoming()

    def get_vertices(self):
        return self.vert_dict

    def get_edges(self):
        return self.edge_dict
