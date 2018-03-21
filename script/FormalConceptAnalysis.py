from concepts import Context
import pandas as pd
import numpy as np
from fcaVisualize import *

def graphviz(self, filename=None, directory=None, render=False, view=False, isEdge=False,**kwargs):
    """Return graphviz source for visualizing the lattice graph."""
    return lattice(self, filename, directory, render, view, isEdge, **kwargs)

class FCA(object):
    def __init__(self, nodePropertyList=None, edgePropertyList=None):
        self.fca_node, self.ctx_node = self.createFCA(nodePropertyList)
        self.fca_edge, self.ctx_edge = self.createFCA(edgePropertyList, True)
        self.mapNodeToTypeId = {}

    def createFCA(self, propertyList, isEdge=False):
        # get objs and attrs
        if isEdge is False:
            index = ['{}:{}'.format(elem.get_id(), elem.get_name()) \
                for elem in propertyList]
        else:
            index = ['{}:{}:{}'.format(elem.get_left_node_id(), \
                    elem.get_right_node_id(), elem.get_name()) \
                for elem in propertyList]
        attrs = set()
        attrs.add("\"\"=\"\"")
        for elem in propertyList:
            currAttr = elem.getAttr() 
            for key, val in currAttr.items():
                if key.lower() != "label" and \
                    "{}={}".format(key,val) not in attrs:
                    attrs.add("{}={}".format(key,val))
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
                fca.loc[[df_idx], "\"\"=\"\""] = "X"
        # print(fca)
        if fca.empty:
            ctx = None
        else:
            ctx_string = fca.to_csv()
            ctx = Context.fromstring(ctx_string,frmat='csv')
        return (fca, ctx)

    def createNodesHierachyGraphviz(self, filename):
        if self.ctx_node is not None:
            dot = graphviz(self.ctx_node.lattice, isEdge = False)
            dot.render(filename)

    def createEdgesHierachyGraphviz(self, filename):
        if self.ctx_edge is not None:
            dot = graphviz(self.ctx_edge.lattice, isEdge = True)
            dot.render(filename)

    def createEdgesGraphviz(self, filename):
        if self.ctx_edge is not None:
            edgesdot = ""
            nid = 0
            for concept in self.ctx_edge.lattice._concepts:
                if concept.objects:
                    primaryNodeId = nid
                    edgesdot += """
        subgraph cluster_{} {{
                    style=filled;
                    color=transparent;
                    node [shape = none, label = \"\"];
                    e{} -> e{}_end [ {}, minlen=2, label={} ];
        }};\n""".format(\
                            nid, nid, nid, ", ".join(concept.intent), len(concept.objects))
                    nid += 1
                    for edge in concept.objects:
                        splitIdx = edge.split(":", 2)
                        leftIdx = splitIdx[0]
                        rightIdx = splitIdx[1]
                        edgeLabel = splitIdx[2]
                        edgesdot += "n{} [ label=\"{}\"];\n".format(\
                                nid, edgeLabel.replace("\"", "\\\""))
                        edgesdot += "e{} -> n{} [dir=none];\n".format(primaryNodeId, nid)
                        nid += 1
                    
            dot =   \
            """
    digraph{{
    rankdir=TB
    edge [style=dashed]
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
                    primaryNodeId = nid
                    nodesdot += "n{} [{}, label={}];\n".format(\
                            nid, ", ".join(concept.intent), len(concept.objects))
                    nid += 1
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
                        self.mapNodeToTypeId[nodeIdx] = primaryNodeId
                        nid += 1
                    
            dot =   \
            """
    graph{{
    rankdir=TB
    edge [style=dashed]
    {}
    }}
            """.format(nodesdot)
            with open(filename, 'w') as file:
                file.write(dot)

    def createGraphviz(self, filename):
        nodesdot = ""
        edgesdot = ""
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
                        splitIdx = node.split(":", 1)
                        nodeIdx = splitIdx[0]
                        nodeLabel = splitIdx[1]
                        # record node type to map
                        self.mapNodeToTypeId[nodeIdx] = primaryNodeId
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
            dot =   \
            """
digraph{{
rankdir=TB
{}

{}
}}
            """.format(nodesdot, edgesdot)
            with open(filename, 'w') as file:
                file.write(dot)
