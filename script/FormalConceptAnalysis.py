from concepts import Context
import pandas as pd
import numpy as np
from fcaVisualize import *
import sqlite3

def graphviz(self, filename=None, directory=None, isEdge=False,showLabel=True, **kwargs):
    """Return graphviz source for visualizing the lattice graph."""
    return lattice(self, filename, directory, isEdge, showLabel, **kwargs)

class FCA(object):
    def __init__(self, graph):
        """
        list all self objects
        self.graph
        self.fca_node
        self.ctx_node
        self.fca_edge
        self.ctx_edge
        self.mapNodeToTypeId
        self.mapNodeTypeIdToCtx
        self.mapNodeToName
        self.mapEdgeToTypeId
        self.mapEdgeTypeIdToCtx
        self.mapEdgeToTypeId_EdgeOnly
        self.mapEdgeTypeIdToCtx_EdgeOnly
        """
        self.graph = graph
        nodePropertyList = graph.vert_dict.values()
        edgePropertyList = graph.edge_dict.values()

        self.fca_node, self.ctx_node = self.createFCA(nodePropertyList)
        self.mapNodeToTypeId, self.mapNodeTypeIdToCtx, self.mapNodeToName = self.helpMapNodeToType()

        self.fca_edge, self.ctx_edge = self.createFCA(edgePropertyList, True)

    def outputSchema(self, filename, format='prolog', config=None):
        # extract node and edge type attr
        nodeAttr = config["nodeAttr"]["include"]
        nodeTypeAttr = config["nodeTypeAttr"]["include"]
        edgeTypeAttr = config["edgeTypeAttr"]["include"]
        if self.mapNodeToTypeId is not None:
            if format == "prolog":
                schema = ""
            elif format == "sql":
                conn = sqlite3.connect(filename)
                c = conn.cursor()
                c.execute("DROP TABLE IF EXISTS node")
                c.execute('''CREATE TABLE node
(nodeId INTEGER, nodeTypeId INTEGER, nodeName TEXT, {})'''\
                .format(' TEXT, '.join(\
        list(map(lambda x: "\"" + x + "\"", nodeAttr)))))
                c.execute("DROP TABLE IF EXISTS nodeType")
                c.execute('''CREATE TABLE nodeType
(nodeTypeId INTEGER, {})'''.format(' TEXT, '.join(\
        list(map(lambda x: "\"" + x + "\"", nodeTypeAttr)))))

                c.execute("DROP TABLE IF EXISTS edge")
                c.execute('''CREATE TABLE edge
(edgeId INTEGER, startNodeId INTEGER, endNodeId INTEGER, edgeTypeId INTEGER)''')
                c.execute("DROP TABLE IF EXISTS edgeType")
                c.execute('''CREATE TABLE edgeType
(edgeTypeId INTEGER, {})'''.format(' TEXT, '.join(\
        list(map(lambda x: "\"" + x + "\"", edgeTypeAttr)))))
            # node schema
            for k, v in self.mapNodeToTypeId.items():
                valueToNodeAttr = []
                nodeName = self.mapNodeToName[k]
                nodeObj = self.graph.vert_dict[int(k)]
                for key in nodeAttr:
                    # flag to check whether the key is in the node attr
                    exist = False
                    for derivedAttrKey, derivedAttrVal in nodeObj.get_derived_attr().items():
                        if derivedAttrKey == key:
                            valueToNodeAttr.append(str(derivedAttrVal))
                            exist = True
                            break
                    if not exist:
                        valueToNodeAttr.append("default")
                if format == "prolog":
                    schema += "#node(nodeId, nodeTypeId, nodeName, {})\n".format(', '.join(nodeAttr))
                    schema += "node(n{}, nt{}, {}, {})\n"\
                               .format(k,v, nodeName, ", ".join(valueToNodeAttr))
                elif format == "sql":
                    query = "INSERT INTO node VALUES (?,?,?{})"\
                             .format(",?"*len(nodeAttr))
                    c.execute(query,[k,v,nodeName] + valueToNodeAttr)
            for k, v in self.mapNodeTypeIdToCtx.items():
                valueToNodeAttr = []
                for key in nodeTypeAttr:
                    # flag to check whether the key is in the node attr
                    exist = False
                    for nodeAttr in v.intent:
                        nodeAttrKey, nodeAttrVal = nodeAttr.split("=")
                        if nodeAttrKey == key:
                            valueToNodeAttr.append(nodeAttrVal)
                            exist = True
                            break
                    if not exist:
                        valueToNodeAttr.append("default")
                if format == "prolog":
                    schema += "#nodeType(nodeTypeId, {})\n".format(', '.join(nodeTypeAttr))
                    schema += "nodeType(nt{}, {})\n"\
                           .format(k, ", ".join(valueToNodeAttr))
                elif format == "sql":
                    query = "INSERT INTO nodeType VALUES (?{})".format(",?"*len(nodeTypeAttr))
                    c.execute(query,[k] + valueToNodeAttr)
            # edge schema
            eid = 0
            for k, v in self.mapEdgeToTypeId.items():
                leftIdx, rightIdx, _ = k.split(":", 2)
                leftTypeIdx, rightTypeIdx, _ = v.split(":", 2)
                edgeTypeIdx = self.mapEdgeToTypeId_EdgeOnly[k]
                if format == "prolog":
                    schema += "#edge(edgeId, startNodeId, endNodeId, edgeTypeId)\n"
                    schema += "edge(e{}, n{}, n{}, et{})\n"\
                        .format(eid, leftIdx, rightIdx, edgeTypeIdx)
                elif format == "sql":
                    c.execute("INSERT INTO edge VALUES (?,?,?,?)",\
                        [eid, leftIdx, rightIdx, edgeTypeIdx])
                eid += 1
            for k, v in self.mapEdgeTypeIdToCtx_EdgeOnly.items():
                # get value from intent
                valueToEdgeAttr = []
                for key in edgeTypeAttr:
                    # flag to check whether the key is in the node attr
                    exist = False
                    for edgeAttr in v.intent:
                        edgeAttrKey, edgeAttrVal = edgeAttr.split("=")
                        if edgeAttrKey == key:
                            valueToEdgeAttr.append(edgeAttrVal)
                            exist = True
                            break
                    if not exist:
                        valueToEdgeAttr.append("default")
                # get edge type idx
                edgeTypeIdx = list(self.mapEdgeTypeIdToCtx_EdgeOnly.keys()).index(k)
                if format == "prolog":
                    schema += "#edgeType(edgeTypeId, {})\n".format(", ".join(edgeTypeAttr))
                    schema += "edgeType(et{}, {})\n"\
                           .format(edgeTypeIdx, ", ".join(valueToEdgeAttr))
                elif format == "sql":
                    query = "INSERT INTO edgeType VALUES (?{})".format(",?"*len(edgeTypeAttr))
                    c.execute(query, [edgeTypeIdx] + valueToEdgeAttr)
            if format == "prolog":
                with open(filename, 'w') as file:
                    file.write(schema)
            elif format == "sql":
                conn.commit()
                conn.close()

    def helpMapNodeToType(self):
        mapNodeToTypeId = {}
        mapNodeToName= {}
        mapNodeTypeIdToCtx = {}
        if self.ctx_node is not None:
            tid = 0
            for concept in self.ctx_node.lattice._concepts:
                if concept.objects:
                    for node in concept.objects:
                        # get node id and label
                        nodeIdx, nodeLabel = node.split(":", 1)
                        # record node type to map
                        mapNodeToTypeId[nodeIdx] = tid
                        mapNodeToName[nodeIdx] = nodeLabel 
                    mapNodeTypeIdToCtx[tid] = concept
                    tid += 1
        return mapNodeToTypeId, mapNodeTypeIdToCtx, mapNodeToName

    def extractIndex(self, propertyList, isEdge):
        # get objs and attrs
        if isEdge is False:
            index = ['{}:{}'.format(elem.get_id(), elem.get_name()) \
                for elem in propertyList]
        else:
            index = ['{}:{}:{}'.format(elem.get_left_node_id(), \
                    elem.get_right_node_id(), elem.get_name()) \
                for elem in propertyList]
        return index

    def extractAttrs(self, propertyList):
        attrs = set()
        for elem in propertyList:
            currAttr = elem.getAttr() 
            for key, val in currAttr.items():
                if key.lower() != "label" and \
                    "{}={}".format(key,val) not in attrs:
                    attrs.add("{}={}".format(key,val))
        return attrs

    def createFCA(self, propertyList, isEdge=False):
        index = self.extractIndex(propertyList, isEdge)
        attrs = self.extractAttrs(propertyList)
        # create FCA
        fca = pd.DataFrame(index=index, columns=attrs)
        fca = fca.fillna("") # with 0s rather than NaNs
        for elem in propertyList:
            if isEdge is False:
                df_idx = '{}:{}'.format(elem.get_id(), elem.get_name())
            else:
                df_idx = '{}:{}:{}'.format(elem.get_left_node_id(), \
                    elem.get_right_node_id(), elem.get_name()) 
            currAttr = elem.getAttr() 
            label = None
            if len(currAttr):
                for key, val in currAttr.items():
                    if key.lower() != "label":
                        fca.loc[[df_idx], "{}={}".format(key,val)] = "X"
                    elif val != "\"\"" and val != "\'\'":
                        label = val
                if label is not None and isEdge is False:
                    fca = fca.rename(index={\
                            df_idx: '{}:{}'.format(elem.get_id(), label)})
            else:
                fca.loc[[df_idx], "attr=default"] = "X"
        #print(fca)
        if fca.empty:
            ctx = None
        else:
            ctx_string = fca.to_csv()
            ctx = Context.fromstring(ctx_string,frmat='csv')
        return (fca, ctx)

    def createNodesHierarchyGraphviz(self, filename, showLabel = True):
        if self.ctx_node is not None:
            dot = graphviz(self.ctx_node.lattice, isEdge = False, showLabel = showLabel)
            dot.save(filename)

    def createEdgesHierarchyGraphviz(self, filename, showLabel=True):
        if self.ctx_edge is not None:
            dot = graphviz(self.ctx_edge.lattice, isEdge = True, showLabel = showLabel)
            dot.save(filename)

    def getDictKey(self, edge, concept):

        # dict "startypeid:endtypeid:attr": number
        leftIdx, rightIdx, edgeLabel = edge.split(":", 2)
        leftNodeCtxId = self.mapNodeToTypeId[leftIdx]
        rightNodeCtxId = self.mapNodeToTypeId[rightIdx]
        # form the keys
        dictKey = '{}:{}:{}'.format(
                leftNodeCtxId, rightNodeCtxId, 
                ",".join(concept.intent))
        return dictKey

    def groupEdgeDicts(self):
        self.mapEdgeToTypeId = {}
        self.mapEdgeToTypeId_EdgeOnly = {}
        self.mapEdgeTypeIdToCtx = {}
        self.mapEdgeTypeIdToCtx_EdgeOnly = {}
        endPointTypeDict = {}
        for idx, concept in enumerate(self.ctx_edge.lattice._concepts):
            if concept.objects:
                # get all pair of start vtx, end vtx type
                for edge in concept.objects:
                    dictKey = self.getDictKey(edge, concept)
                    if dictKey in endPointTypeDict:
                        endPointTypeDict[dictKey] += 1
                    else:
                        endPointTypeDict[dictKey] = 1
                    # store the edge to the global map for output
                    self.mapEdgeToTypeId[edge] = dictKey
                    self.mapEdgeToTypeId_EdgeOnly[edge] = idx
                    self.mapEdgeTypeIdToCtx[dictKey] = concept
                self.mapEdgeTypeIdToCtx_EdgeOnly[idx] = concept
        return endPointTypeDict

    def drawEdgesWithAttrs(self, endPointTypeDict, nid):
        edgesdot = ""
        # draw the edges with the grouped type
        for endPointType, count in endPointTypeDict.items():
            eid = list(endPointTypeDict.keys()).index(endPointType)
            splitIdx = endPointType.split(":", 2)
            leftIdx = int(splitIdx[0])
            rightIdx = int(splitIdx[1])
            edgeAttr = splitIdx[2]
            leftnodesdot = "e{}_start [{}, label=\" \"];\n".format(\
                    eid, ", ".join(self.mapNodeTypeIdToCtx[leftIdx].intent))
            rightnodesdot = "e{}_end [{}, label=\" \"];\n".format(\
                    eid, ", ".join(self.mapNodeTypeIdToCtx[rightIdx].intent))
            edgesdot += """
subgraph cluster_{} {{
    style=filled;
    color=transparent;
    """.format(nid)
            edgesdot += leftnodesdot
            edgesdot += rightnodesdot
            edgesdot += """
    e{0}_start -> e{0}_end [ {1}, minlen=2, label={2} ];
    e{0}_inv [style=invis]
    e{0}_start -> e{0}_inv [style=invis]
    e{0}_end -> e{0}_inv [style=invis]
}};
            \n""".format(\
                    eid, edgeAttr, count)
            nid += 1
        return (edgesdot, nid)

    def drawEdgesWithNames(self, endPointTypeDict, nid):
        edgesdot = ""
        for concept in self.ctx_edge.lattice._concepts:
            if concept.objects:
                # draw edges that have the parent attributes
                for edge in concept.objects:
                    dictKey = self.getDictKey(edge, concept)
                    edgeLabel = edge.split(":", 2)[2]
                    eid = list(endPointTypeDict.keys()).index(dictKey)
                    edgesdot += "n{} [ label=\"{}\"];\n".format(\
                            nid, edgeLabel.replace("\"", "\\\""))
                    edgesdot += "e{}_inv -> n{} [dir=none, style=dashed];\n".format(eid, nid)
                    nid += 1
        return edgesdot, nid

    def createEdgesGraphviz(self, filename):
        #TODO: deal with undirected graph
        if self.ctx_edge is not None:
            endPointTypeDict = self.groupEdgeDicts()
            edgesdot = ""
            nid = 0
            # self.drawEdgesWithAttrs
            edgeTypeAttrDot, nid = self.drawEdgesWithAttrs(endPointTypeDict, nid)
            edgesdot += edgeTypeAttrDot
            # drawEdgesWithNames
            edgeTypeNameDot, nid = self. drawEdgesWithNames(endPointTypeDict, nid)
            edgesdot += edgeTypeNameDot
            # output formated dot file
            dot =   \
            """
digraph{{
rankdir=LR
{}
}}
            """.format(edgesdot)
            with open(filename, 'w') as file:
                file.write(dot)
        
    def createNodesGraphviz(self, filename):
        if self.ctx_node is not None:
            nodesdot = ""
            nid = 0
            for concept in self.ctx_node.lattice._concepts:
                if concept.objects:
                    # draw nodes with the type attr
                    primaryNodeId = nid
                    nodesdot += "n{} [{}, label={}];\n".format(\
                            nid, ", ".join(concept.intent), len(concept.objects))
                    nid += 1
                    # draw nodes with names
                    for node in concept.objects:
                        # get node id and label
                        splitIdx = node.split(":", 1)
                        nodeIdx = splitIdx[0]
                        nodeLabel = splitIdx[1]
                        # add node to dot
                        nodesdot += "n{} [{}, label={}];\n".format(\
                                nid, ", ".join(concept.intent), nodeLabel)
                        nodesdot += "n{} -- n{};\n".format(primaryNodeId, nid)
                        # record node type to map
                        nid += 1
                    
            dot =   \
            """
graph{{
rankdir=LR
edge [style=dashed]
{}
}}
            """.format(nodesdot)
            with open(filename, 'w') as file:
                file.write(dot)

    def helpDrawFullGraphvizNodesDot(self):
        nodesdot = ""
        if self.ctx_node is not None:
            nid = 0
            for concept in self.ctx_node.lattice._concepts:
                if concept.objects:
                    primaryNodeId = nid
                    nodesdot += "n{} [{}, label={}];\n".format(\
                            nid, ", ".join(concept.intent), len(concept.objects))
                    nid += 1
                    for node in concept.objects:
                        # get node id and label
                        nodeIdx, nodeLabel = node.split(":", 1)
                        # record node type to map
                        self.mapNodeToTypeId[nodeIdx] = primaryNodeId
        return nodesdot

    def helpDrawFullGraphvizEdgesDot(self):
        edgesdot = ""
        if self.ctx_edge is not None:
            nid = 0
            for concept in self.ctx_edge.lattice._concepts:
                countEdge = {}
                for concObj in  concept.objects:
                    splitIdx = concObj.split(":", 2)
                    leftIdx = self.mapNodeToTypeId[splitIdx[0]]
                    rightIdx = self.mapNodeToTypeId[splitIdx[1]]
                    key = 'n{} -> n{}'.format(leftIdx, rightIdx)
                    if key in countEdge:
                        countEdge[key] += 1
                    else:
                        countEdge[key] = 1
                for key, val in countEdge.items():
                    edgesdot += """
{} [ {}, minlen=2, label={} ];\n""".format(\
                            key, ", ".join(concept.intent), val)
        return edgesdot

    def createGraphviz(self, filename):
        nodesdot = self.helpDrawFullGraphvizNodesDot()
        edgesdot = self.helpDrawFullGraphvizEdgesDot()
        dot =   \
        """
digraph{{
rankdir=LR
{}

{}
}}
        """.format(nodesdot, edgesdot)
        with open(filename, 'w') as file:
            file.write(dot)
