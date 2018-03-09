import copy
from objdict import ObjDict
import matplotlib.pyplot as plt

class TypeHierachy(object):
    def __init__(self,root):
        self.root = root
        self.nodeId = 0
        self.edgeId = 0
        # indexed by level
        self.typeNodes = {}
        self.typeEdges = {}

        self.constructTypeHierachy()
        self.visualize()

    def constructTypeHierachy(self):
        # empty set
        self.typeNodes[0] = [TypeNode(None, 0, self.nodeId)]
        self.nodeId += 1

        # one element in set
        self.typeNodes[1] = []
        self.typeEdges[1] = []
        for nodeType, nodeVal in self.root.items():
            newNode = TypeNode({nodeType: nodeVal}, 1, self.nodeId)
            self.typeNodes[1].append(newNode)
            self.typeEdges[1].append((0, self.nodeId))
            self.nodeId += 1

        # build multiple level based on the information in the previous level
        # | {A (a1, a2), B (b1, b2)} | {C (c1, c2), B (b1, b3)} | => {A (a1, a2), B (b1), C (c1, c2)}
        numLevel = len(self.typeNodes[1])
        baseLevelNodes = self.typeNodes[1]
        # iterate through levels
        for level in range(2, numLevel+1):
            # a set of forzenset representing currentSet in the list
            setOfSets = set()

            self.typeNodes[level] = []
            self.typeEdges[level] = []
            lastLevelNodes = self.typeNodes[level-1]
            # iterate through the first set
            for firstSet in range(len(lastLevelNodes)):
                # iterate through the second set
                for secondSet in range(len(baseLevelNodes)):
                    # get dictionaries
                    newValToEle = copy.deepcopy(\
                            lastLevelNodes[firstSet].typeValsToEleId)
                    valToEle2 = copy.deepcopy(\
                            baseLevelNodes[secondSet].typeValsToEleId)
                    # get key sets union
                    for key, value in valToEle2.items():
                        if key not in newValToEle:
                            newValToEle[key] = value

                    # check whether the type node has already added
                    if(len(newValToEle.keys()) == level and \
                            frozenset(newValToEle.keys()) not in setOfSets ):
                        # create new node
                        newNode = TypeNode(newValToEle, level, self.nodeId)
                        if (len(newNode.typeValsToEleId) == level):
                            # add new type Node
                            self.typeNodes[level].append(newNode)
                            setOfSets.add(frozenset(newValToEle.keys()))
                            self.typeEdges[1].append((lastLevelNodes[firstSet].nodeId, newNode.nodeId))
                            self.nodeId += 1
        self.printCombinations()

    def printCombinations(self):
        # check combinatin of val of every pair of nodes
        for i in range(len(self.typeNodes)):
            print("level {}".format(i))
            for j in range(len(self.typeNodes[i])):
                print(self.typeNodes[i][j].typeValsToEleId)

class TypeNode(object):
    """
        Record the shared elements by different node types.
        typeSet: a set of types
        typeValsToEleId: value to element dictionary. value is a tuple
    {
    a: {aa:[1,2], 
           ab[3]}
    b: {ba: [0],
        bb: [1]}
    }
    =>
    {
    a: {aa:[1]} 
    b: {
        bb: [1]}
    }
    """
    def __init__(self, dictType, level, nodeId):
        #self.propertyList = propertyList
        self.typeValsToEleId = dictType 
        self.level = level
        self.nodeId = nodeId
        # typeVals
        if dictType is None: self.typeSet = set()
        else:
            self.typeSet = set(dictType.keys())
            # key typeVal: value: set of nodeid
            self.constructTypeValsToEleId(dictType)
        self.inEdges = {}
        self.outEdges = {}


    def constructTypeValsToEleId(self, mapping):
        # map key is type, map value is ObjDict of type values
        isSetAllEle = False
        # check whether the map is empty
        if mapping is not None:
            # get eleId in node
            allEleIds = set()
            for nodeType, typeVals in mapping.items():
                # get all ids under a type
                allEleInType = set()
                for typeVal, eleIds in typeVals.items():
                    allEleInType |= set(eleIds)
                if isSetAllEle is False:
                    allEleIds |= allEleInType
                    isSetAllEle = True
                else:
                    allEleIds &= allEleInType
        self.delElementNotShared(mapping, allEleIds)
        self.delEmptyKeyValPair(mapping)

    def delEmptyKeyValPair(self, mapping):
        copyMap = copy.deepcopy(mapping)
        for key, val in copyMap.items():
            if(len(val) == 0):
                del mapping[key]

    def delElementNotShared(self, mapping, allEleIds):
        # delete elements that are not shared by all nodes
        if mapping is not None:
            for nodeType, typeVals in mapping.items():
                # typeVal is an ObjDict
                for typeVal, eleIds in typeVals.items():
                    # eleIds is a list
                    idx = 0
                    while idx < len(eleIds):
                        if eleIds[idx] not in allEleIds:
                            del eleIds[idx]
                        else:
                            idx += 1
            self.delEmptyTypeVals(mapping)

    def delEmptyTypeVals(self, mapping):
        if mapping is not None:
            for nodeType, typeVals in mapping.items():
                # reconstruct objdict
                newDict = ObjDict()
                for typeVal, eleIds in typeVals.items():
                    if(len(eleIds) != 0):
                        newDict[typeVal] = eleIds
                mapping[nodeType] = newDict
        
class TypeEdge(object):
    def __init__(self, fromType, fromVal, toType, toVal, eleId):
        self.fromType = fromType
        self.fromVal = fromVal
        self.toType = toType
        self.toVal = toVal
        self.eleId = eleId
