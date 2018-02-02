from  GraphObj  import *

class GraphProperties():
    def __init__(self):
        self.currAttr = {}
        self.elementList = []
        self.newId = 0
        self.isTempAttr = 0

    def getCurrAttr(self):
        return self.currAttr

    def addCurrAttr(self, obj, val):
        self.currAttr[obj] = val

    def deleteCurrAttrKey(self, key):
        self.currAttr.pop(key, None)

    def appendList(self, obj):
        self.elementList.append(obj)

    def getElementList(self):
        return self.elementList

    def getNewId(self):
        return self.newId

    def getIsTempAttr(self):
        return self.isTempAttr

    def setIsTempAttr(self, num):
        self.isTempAttr = num

    def incId(self):
        self.newId += 1

    def update(self, key, val, update_method):
        if self.getIsTempAttr() == 1:
            # if "node_id [attr_list] "
            update_method(key, val)
        else:
            # if "node [attr_list] "
            self.addCurrAttr(key, val)

    def flushNewObj(self):
        self.isTempAttr = 0
        self.incId()

class NodeProperties(GraphProperties):
    def __init__(self):
        GraphProperties.__init__(self)
        self.currNode = None

    def setCurrNodeName(self, obj):
        
        self.currNode.set_name(obj)

    def addNewNode(self):
        self.isTempAttr = 1
        self.currNode = GraphNode(self.getNewId(), self.currAttr)

    # callback function
    def update_attr(self, key, val):
        self.currNode.addAttr(key, val)

    def update(self, key, val, update_method=None):
        super().update(key, val, self.update_attr)

    def flushNewNode(self):
        super().flushNewObj()
        self.appendList(self.currNode)
        self.currNode = None
        
class EdgeProperties(GraphProperties):
    def __init__(self):
        GraphProperties.__init__(self)
        self.currLeftNodeName = None
        self.currRightNodeName = None
        self.currEdge = None

    def setCurrLeftNodeName(self, obj):
        self.currLeftNodeName = obj

    def getCurrLeftNodeName(self):
        return self.currLeftNodeName

    def setCurrRightNodeName(self, obj):
        self.currRightNodeName = obj

    def getCurrRightNodeName(self):
        return self.currRightNodeName

    def addNewEdge(self):
        self.isTempAttr = 1
        self.currEdge = GraphEdge(self.getNewId(), self.currAttr)

    # callback function
    def update_attr(self, key, val):
        self.currEdge.addAttr(key, val)

    def update(self, key, val, update_method=None):
        super().update(key, val, self.update_attr)

    def flushNewEdge(self):
        super().flushNewObj()
        self.appendList(self.currEdge)
        self.currEdge = None
