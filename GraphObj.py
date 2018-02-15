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

    def printNode(self):
        print("id:{}\nname:{}\nattr:{}\n".format(self.get_id(), self.name, self.attr))
    def getAttrVal(self, key):
        return self.attr[key]


class GraphNode(GraphObj):
    def __init__(self, id, attr_list=None):
        super().__init__(id, attr_list)
        self.name = None
        
    def get_name(self):
        return self.name

    def set_name(self, x):
        self.name = x

class GraphEdge(GraphObj):
    def __init__(self, id, attr_list=None):
        super().__init__(id, attr_list)
        self.left_node = None
        self.right_node = None
        self.directed = None
