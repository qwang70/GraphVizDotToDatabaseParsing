import copy

class GraphObj(object):
    def __init__(self, id, attr_list=None):
        self.id = id
        self.attr = copy.deepcopy(attr_list)
        self.attr_type = None

    def get_id(self):
        return self.id

    def set_id(self, x):
        self.id = x

    def getAttr(self):
        return self.attr

    def setAttr(self, obj):
        self.attr = obj

    def addAttr(self, key, val):
        self.attr[key] = val

    def getAttrVal(self, key):
        return self.attr[key]


class GraphNode(GraphObj):
    def __init__(self, id, attr_list=None):
        super().__init__(id, attr_list)
        self.name = None

        # fill on second iteration
        self.adjacentEdge = []
        self.incoming = 0
        self.outgoing = 0

    def get_name(self):
        return self.name

    def set_name(self, x):
        self.name = x
    
    def printNode(self):
        print("id:{}\nname:{}\nattr:{}\n".format(self.get_id(), self.name, self.attr))

    # from second graph iteration
    def add_neighbor(self, edge):
        self.adjacentEdge.append(edge.get_id())

    def add_neighbor_id(self, eid):
        self.adjacentEdge.append(eid)

    def get_derived_attr(self):
        return self.derived_attr
    def gen_derived_attr(self):
        self.derived_attr = {}
        if self.incoming > 0:
            self.derived_attr["indeg>0"] = True
        else:
            self.derived_attr["indeg>0"] = False
        self.derived_attr["indeg"] = self.incoming
        if self.outgoing > 0:
            self.derived_attr["outdeg>0"] = True
        else:
            self.derived_attr["outdeg>0"] = False
        self.derived_attr["outdeg"] = self.outgoing
        
    def incIncoming(self):
        self.incoming += 1

    def incOutgoing(self):
        self.outgoing += 1

class GraphEdge(GraphObj):
    def __init__(self, id, attr_list=None):
        super().__init__(id, attr_list)
        self.left_node = None
        self.right_node = None
        self.left_node_id = -1
        self.right_node_id = -1
        self.directed = None

    def set_directed(self, directed):
        self.directed = directed

    def get_directed(self):
        return self.directed
    def set_left_node_name(self, obj):
        self.left_node = obj

    def get_left_node_name(self):
        return self.left_node

    def set_right_node_name(self, obj):
        self.right_node = obj

    def get_right_node_name(self):
        return self.right_node

    def set_left_node_id(self, obj):
        self.left_node_id = obj

    def get_left_node_id(self):
        return self.left_node_id

    def set_right_node_id(self, obj):
        self.right_node_id = obj

    def get_right_node_id(self):
        return self.right_node_id

    def get_name(self):
        if self.directed:
            return '{} -> {}'.format(self.left_node, self.right_node) 
        else:
            return '{} -- {}'.format(self.left_node, self.right_node) 

    def printNode(self):
        print("id:{}\n{} left:{} right:{}\nattr:{}\n".format(self.get_id(), self.directed, self.left_node, self.right_node, self.attr))
