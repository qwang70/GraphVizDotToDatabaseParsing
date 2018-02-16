import copy

class TypeHierachy(object):
    def __init__(self,root, propertyList):
        self.root = root
        # indexed by level
        self.typeNodes = {}
        self.typeEdges = {}

        # empty set
        self.typeNodes[0] = [TypeNode(None, 0)]

        # one element in set
        self.typeNodes[1] = []
        # self.typeEdges[1] = []
        for nodeType, nodeVal in root.items():
            self.typeNodes[1].append(
                TypeNode({nodeType: nodeVal}, 1, propertyList))

        # build multiple level based on the information in the previous level
        # | {A (a1, a2), B (b1, b2)} | {C (c1, c2), B (b1, b3)} | => {A (a1, a2), B (b1), C (c1, c2)}
        numLevel = len(self.typeNodes[1])
        # iterate through levels
        for level in range(2, numLevel):
            lastLevelNodes = self.typeNodes[level-1]
            # iterate through the first set
            for firstSet in range(len(lastLevelNodes)):
                # iterate through the second set
                for secondSet in range(firstSet+1, len(lastLevelNodes)):
                    #TODO: order the typeNodes through defining a comparison function
                    # get dictionaries
                    newValToEle = copy.deepcopy(lastLevelNodes[firstSet].typeValsToEleId)
                    valToEle2 = lastLevelNodes[secondSet].typeValsToEleId
                    #print(valToEle1)

                    # get key sets union
                    for key, value in valToEle2.items():
                        if key not in newValToEle:
                            newValToEle[key] = value
                    # TODO: check if key nset no in pairs
                    print(newValToEle)
                    TypeNode(newValToEle, level, propertyList)


            # check combinatin of val of every pair of nodes
        for i in range(len(self.typeNodes[1])):
            print(self.typeNodes[1][i].typeValsToEleId)
            
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
        {aa,bb}: 1
    }
    """
    def __init__(self, dictType, level, propertyList=None):
        self.propertyList = propertyList
        self.typeValsToEleId = {}
        # typeVals
        if dictType is None: self.typeSet = set()
        else:
            self.typeSet = set(dictType.keys())
            # key typeVal: value: set of nodeid
            self.constructTypeValsToEleId(dictType)
        self.inEdges = {}
        self.outEdges = {}

        self.level = level

    def constructTypeValsToEleId(self, mapping):
        isSetAllEle = False
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
        # pack attribute value into a set
        for eleId in allEleIds:
            # get value from attribute list
            valSet = set()
            for attKey in self.typeSet:
                valSet = valSet | {self.propertyList[eleId].getAttrVal(attKey)}
            if tuple(valSet) not in self.typeValsToEleId:
                self.typeValsToEleId[tuple(valSet)] = {eleId}
            else:
                self.typeValsToEleId[tuple(valSet)] |= {eleId}

class TypeEdge(object):
    def __init__(self, fromType, fromVal, toType, toVal, eleId):
        self.fromType = fromType
        self.fromVal = fromVal
        self.toType = toType
        self.toVal = toVal
        self.eleId = eleId
