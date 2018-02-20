import copy
from objdict import ObjDict

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
        for level in range(2, numLevel+1):
            print("level " , level)
            self.typeNodes[level] = []
            lastLevelNodes = self.typeNodes[level-1]
            # iterate through the first set
            for firstSet in range(len(lastLevelNodes)):
                # iterate through the second set
                for secondSet in range(firstSet+1, len(lastLevelNodes)):
                    #TODO: order the typeNodes through defining a comparison function
                    # get dictionaries
                    newValToEle = copy.deepcopy(lastLevelNodes[firstSet].typeValsToEleId)
                    valToEle2 = lastLevelNodes[secondSet].typeValsToEleId
                    

                    # get key sets union
                    for key, value in valToEle2.items():
                        if key not in newValToEle:
                            # TODO: merge not override existing key
                            newValToEle[key] = value
                    # TODO: check if key nset no in pairs
                    self.typeNodes[level].append(\
                        TypeNode(newValToEle, level, propertyList))
            for j in range(len(self.typeNodes[level])):
                print(self.typeNodes[level][j].typeValsToEleId)


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
    def __init__(self, dictType, level, propertyList=None):
        self.propertyList = propertyList
        self.typeValsToEleId = dictType 
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
        """
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
        """
        self.delElementNotShared(mapping, allEleIds)

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
