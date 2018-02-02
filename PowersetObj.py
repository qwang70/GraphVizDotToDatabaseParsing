class TypeHierachy(object):
    def __init__(self,root=None):
        self.root = root

class TypeNode(object):
    def __init__(self, dictType):
        self.typeSet = set(dictType.keys())
        self.typeToValsDict = dictType
