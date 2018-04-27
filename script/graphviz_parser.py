import sqlite3
import copy
from antlr4.tree.Tree import TerminalNodeImpl
from antlr4 import *
from DOTLexer import DOTLexer
from DOTListener import DOTListener
from DOTParser import DOTParser
import os, sys
import argparse

from objdict import ObjDict
import json

# class
from GraphProperties import *
from PowersetObj import *
from FormalConceptAnalysis import *
from parse_json import *
from Graph import *

class TreeNode(object):
    def __init__(self, id):
        self.id = id
        self.children = []
        self.parent = None

    def setId(self, obj):
        self.id = obj
        
    def getId(self):
        return self.id

    def add_child(self, obj):
        self.children.append(obj)
        
    def getChild(self, childIdx):
        return self.children[childIdx]
    
    def getChildren(self):
        return self.children

    def setParent(self, obj):
        self.parent = obj
        
    def getParent(self):
        return self.parent

class DOTPrintListener(DOTListener):
    def __init__(self):
        # can be delete
        self.numToken = 0
        self.copyTree = None
        self.currTreeNode = None

        # attribute list related
        self.nodeProperties = NodeProperties()
        self.edgeProperties = EdgeProperties()

        # mode
        # GRAPH: 0, NODE: 1, EDGE: 2
        self.currAttrType = 0

    def getNodeProperties(self):
        return self.nodeProperties

    def getEdgeProperties(self):
        return self.edgeProperties

    def enterGraph(self, ctx):
        pass
        
    def exitGraph(self, ctx):
        for edgeIdx in range(len(self.edgeProperties.elementList)):
            edge = self.edgeProperties.elementList[edgeIdx]
            count = 0
            for node in self.nodeProperties.elementList:
                if count >= 2:
                    break
                if edge.get_left_node_name() == node.get_name():
                    edge.set_left_node_id ( node.get_id() )
                    count += 1
                if edge.get_right_node_name() == node.get_name():
                    edge.set_right_node_id ( node.get_id() )
                    count += 1
            assert edge.get_left_node_id() != -1 and edge.get_right_node_id() != -1
            self.edgeProperties.elementList[edgeIdx] = edge
        #    self.nodeProperties.elementList[i].printNode()

    # Enter a parse tree produced by DOTParser#stmt_list.
    def enterStmt_list(self, ctx:DOTParser.Stmt_listContext):
        pass

    # Exit a parse tree produced by DOTParser#stmt_list.
    def exitStmt_list(self, ctx:DOTParser.Stmt_listContext):
        pass


    # Enter a parse tree produced by DOTParser#stmt.
    def enterStmt(self, ctx:DOTParser.StmtContext):
        pass

    # Exit a parse tree produced by DOTParser#stmt.
    def exitStmt(self, ctx:DOTParser.StmtContext):
        pass


    # Enter a parse tree produced by DOTParser#attr_stmt.
    def enterAttr_stmt(self, ctx:DOTParser.Attr_stmtContext):
        
        # change CeurrAttrType
        if ctx.GRAPH() is not None:
            self.currAttrType = 0
        elif ctx.NODE() is not None:
            self.currAttrType = 1
        elif ctx.EDGE() is not None:
            self.currAttrType = 2

    # Exit a parse tree produced by DOTParser#attr_stmt.
    def exitAttr_stmt(self, ctx:DOTParser.Attr_stmtContext):
        self.currAttrType = 0

    # Enter a parse tree produced by DOTParser#attr_list.
    def enterAttr_list(self, ctx:DOTParser.Attr_listContext):
        pass

    # Exit a parse tree produced by DOTParser#attr_list.
    def exitAttr_list(self, ctx:DOTParser.Attr_listContext):
        pass


    # Enter a parse tree produced by DOTParser#a_list.
    def enterA_list(self, ctx:DOTParser.A_listContext):
        pass

    # Exit a parse tree produced by DOTParser#a_list.
    def exitA_list(self, ctx:DOTParser.A_listContext):

        for i in range(ctx.getChildCount()):
            # check whether the child is a terminal TreeNode
            if type(ctx.getChild(i)) is TerminalNodeImpl and ctx.getChild(i).getText() == '=':
                assert (type(ctx.getChild(i-1)) is DOTParser.Id_declContext
                        and type(ctx.getChild(i+1)) is DOTParser.Id_declContext)
                key = ctx.getChild(i-1).getText()
                val = ctx.getChild(i+1).getText()

                # if "node [attr_list] "
                if self.currAttrType == 1:
                    self.nodeProperties.update(key, val)
                elif self.currAttrType == 2:
                    self.edgeProperties.update(key, val)
                    
    # Enter a parse tree produced by DOTParser#edge_stmt.
    def enterEdge_stmt(self, ctx:DOTParser.Edge_stmtContext):
        self.edgeProperties.addNewEdge()
        self.currAttrType = 2

    # Exit a parse tree produced by DOTParser#edge_stmt.
    def exitEdge_stmt(self, ctx:DOTParser.Edge_stmtContext):
        self.edgeProperties.flushNewEdge()
        self.currAttrType = 0


    # Enter a parse tree produced by DOTParser#edgeRHS.
    def enterEdgeRHS(self, ctx:DOTParser.EdgeRHSContext):
        pass

    # Exit a parse tree produced by DOTParser#edgeRHS.
    def exitEdgeRHS(self, ctx:DOTParser.EdgeRHSContext):
        pass

    # Enter a parse tree produced by DOTParser#edgeop.
    def enterEdgeop(self, ctx:DOTParser.EdgeopContext):
        if ctx.getText() == "--":
            self.edgeProperties.setDirected(False)
        elif ctx.getText() == "->":
            self.edgeProperties.setDirected(True)

    # Exit a parse tree produced by DOTParser#edgeop.
    def exitEdgeop(self, ctx:DOTParser.EdgeopContext):
        pass

    # Enter a parse tree produced by DOTParser#Node_stmt.
    def enterNode_stmt(self, ctx:DOTParser.Node_stmtContext):
        self.nodeProperties.addNewNode()
        self.currAttrType = 1

    # Exit a parse tree produced by DOTParser#Node_stmt.
    def exitNode_stmt(self, ctx:DOTParser.Node_stmtContext):
        self.nodeProperties.flushNewNode()
        self.currAttrType = 0

    # Enter a parse tree produced by DOTParser#Node_id.
    def enterNode_id(self, ctx:DOTParser.Node_idContext):
        if self.nodeProperties.getIsTempAttr() == 1:
            self.nodeProperties.setCurrNodeName(ctx.getText())
        elif self.edgeProperties.getIsTempAttr() == 1:
            self.edgeProperties.setCurrLeftNodeName(ctx.getText())
            self.edgeProperties.setIsTempAttr(2);
        elif self.edgeProperties.getIsTempAttr() == 2:
            self.edgeProperties.setCurrRightNodeName(ctx.getText())

    # Exit a parse tree produced by DOTParser#Node_id.
    def exitNode_id(self, ctx:DOTParser.Node_idContext):
        pass


    # Enter a parse tree produced by DOTParser#port.
    def enterPort(self, ctx:DOTParser.PortContext):
        pass

    # Exit a parse tree produced by DOTParser#port.
    def exitPort(self, ctx:DOTParser.PortContext):
        pass


    # Enter a parse tree produced by DOTParser#subgraph.
    def enterSubgraph(self, ctx:DOTParser.SubgraphContext):
        pass

    # Exit a parse tree produced by DOTParser#subgraph.
    def exitSubgraph(self, ctx:DOTParser.SubgraphContext):
        pass


    # Enter a parse tree produced by DOTParser#id_decl.
    def enterId_decl(self, ctx:DOTParser.Id_declContext):
        pass

    # Exit a parse tree produced by DOTParser#id_decl.
    def exitId_decl(self, ctx:DOTParser.Id_declContext):
        pass

def main():
    input_file = args.infile
    base_filename = input_file.split("/")[-1].split(".")[0]
    if args.outFolder:
        output_folder = args.outFolder
    else:
        output_folder = '/'.join(input_file.split("/")[:-2]) + "/output"
    # parse dot/gv file and build idbase
    input_stream = FileStream(input_file)
    lexer = DOTLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DOTParser(stream)
    tree = parser.graph()
    printer = DOTPrintListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

    nodePropertyList = printer.getNodeProperties().getElementList()
    edgePropertyList = printer.getEdgeProperties().getElementList()

    graph = Graph(nodePropertyList, edgePropertyList)

    # fca node
    fca = FCA(graph)
    # create hierarchy graph
    hierarchyFolder = "{}/HierarchyGraph".format(output_folder)
    os.makedirs( hierarchyFolder,exist_ok=True )
    fca.createNodesHierarchyGraphviz(\
            '{}/{}{}'.format(hierarchyFolder, base_filename, "_nodes_hierarchy.gv"), showLabel=False)
    fca.createEdgesHierarchyGraphviz(\
            '{}/{}{}'.format(hierarchyFolder, base_filename,"_edges_hierarchy.gv"), showLabel=False)
    fca.createNodesHierarchyGraphviz(\
            '{}/{}{}'.format(hierarchyFolder, base_filename, "_nodes_hierarchy_with_name.gv"))
    fca.createEdgesHierarchyGraphviz(\
            '{}/{}{}'.format(hierarchyFolder, base_filename,"_edges_hierarchy_with_name.gv"))
    # create type graph
    typeGraphFolder = "{}/TypeGraph".format(output_folder)
    os.makedirs( typeGraphFolder, exist_ok=True )
    fca.createNodesGraphviz(\
            '{}/{}{}'.format(typeGraphFolder, base_filename, "_nodes.gv"))
    fca.createEdgesGraphviz(\
            '{}/{}{}'.format(typeGraphFolder, base_filename, "_edges.gv"))
    fca.createGraphviz(\
            '{}/{}{}'.format(typeGraphFolder, base_filename, "_full.gv"))

    # parse json file
    config = parse_json(args.config)
    fca.outputSchema(\
            '{}/{}{}'.format(output_folder, base_filename, "_schema.txt"), config =config )
    fca.outputSchema(\
            '{}/{}{}'.format(output_folder, base_filename, "_schema.db"), format="sql", config = config )

    # powerset formation
    # createTypeHierarchyGraph(nodePropertyList)

def createTypeHierarchyGraph(propertyList):
    # powerset construction
    commonKeys, structuredDict = preprocessing(propertyList)
    outputJson(structuredDict)

    # typeHierarchy = TypeHierarchy(structuredDict)

def outputJson(structuredDict):
    json_data = structuredDict.dumps(indent=4)
    print(json_data)

def preprocessing(propertyList):
    structuredDict = ObjDict()
    for num, elem in enumerate(propertyList):
        attr = elem.getAttr()
        if num == 0:
            commonKeys = set(attr.keys())
        else:
            commonKeys = commonKeys & set(attr.keys())
        for key, val in attr.items():
            if key not in structuredDict:
                structuredDict[key] = ObjDict() 
            if val not in structuredDict[key]:
                structuredDict[key][val] = [elem.get_name()]
            else:
                structuredDict[key][val].append(elem.get_name())
    return commonKeys, structuredDict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A GraphViz dot file to Sqlite idbase converter.')
    parser.add_argument('-outFolder', 
                        help='name of the output idbase file')
    parser.add_argument('-config', 
                        help='name of the configuration json file')
    parser.add_argument('infile', 
                        help='name of the input dot/gv file')
    args = parser.parse_args()
    main()
