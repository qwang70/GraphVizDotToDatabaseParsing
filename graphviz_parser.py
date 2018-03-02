import sqlite3
import copy
from antlr4.tree.Tree import TerminalNodeImpl
from antlr4 import *
from DOTLexer import DOTLexer
from DOTListener import DOTListener
from DOTParser import DOTParser
import sys
import argparse

from objdict import ObjDict
import json

# class
from GraphProperties import *
from PowersetObj import *
from FormalConceptAnalysis import *

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
    def __init__(self, output_file):
        # can be delete
        self.numToken = 0
        self.copyTree = None
        self.currTreeNode = None

        # attribute list related
        self.nodeProperties = NodeProperties()
        self.edgeProperties = EdgeProperties()
        #??
        self.attrType = {}

        # mode
        # GRAPH: 0, NODE: 1, EDGE: 2
        self.currAttrType = 0

        self.conn = sqlite3.connect(output_file)
        self.c = self.conn.cursor()
        # create tokens table
        self.c.execute("DROP TABLE IF EXISTS tokens")
        self.c.execute("CREATE TABLE tokens(Id integer primary key,token_type text, token_val  text)")

        # create table for searching parent and children
        self.c.execute("DROP TABLE IF EXISTS token_tree")
        self.c.execute("CREATE TABLE token_tree(Id integer,parent_id integer, child_id integer)")

    def getNodeProperties(self):
        return self.nodeProperties

    def getEdgeProperties(self):
        return self.edgeProperties

    def createNewTreeNodeWhileEntering(self):
        # initiate new TreeNode for self
        newTreeNode = TreeNode(self.numToken)
        if self.copyTree is None:
            self.copyTree = newTreeNode
        else:
            newTreeNode.setParent(self.currTreeNode)
            self.currTreeNode.add_child(newTreeNode)
        self.currTreeNode = newTreeNode
        self.numToken += 1

    
    def reassignCurrTreeNode(self):
        # assign the current TreeNode to be its parent TreeNode
        assert self.currTreeNode is not None
        self.currTreeNode = self.currTreeNode.getParent()

    def addToDB(self, ctx, type_val):
        self.c.execute("INSERT INTO tokens VALUES(?, ?, ?)", (self.currTreeNode.getId(), type_val, ctx.getText()))
        # assign parent id
        if self.currTreeNode.getParent() is None: 
            parent_id = None
        else:
            parent_id = self.currTreeNode.getParent().getId()
        # assign a list of child id
        if ctx.getChildCount() == 0:
            child = None
        else:
            child = []
            TreeNodeChildIdx = 0
            for i in range(ctx.getChildCount()):
                # check whether the child is a terminal TreeNode
                #if type(ctx.getChild(i)) is antlr4.tree.Tree.TerminalNodeImpl:
                if type(ctx.getChild(i)) is TerminalNodeImpl:
                    terminalCtx = ctx.getChild(i)
                    #self.c.execute("INSERT INTO tokens VALUES(?,?, ?)", (self.numToken, "symbol", ctx.getText()))
                    self.c.execute("INSERT INTO tokens VALUES(?, ?, ?)", (self.numToken, "terminal", terminalCtx.getText()))
                    self.c.execute("INSERT INTO token_tree VALUES(?, ?, ?)", (self.numToken, self.currTreeNode.id, None))
                    self.numToken += 1
                else:
                    assert TreeNodeChildIdx < ctx.getChildCount()
                    child.append( self.currTreeNode.getChild(TreeNodeChildIdx) )
                    TreeNodeChildIdx += 1
            if len(child) == 0:
                child = None
            # get all combinations of parent and child index
            if child is None:
                col_pair = [(self.currTreeNode.getId(), parent_id, child)]
            else:
                col_pair = [(self.currTreeNode.getId(), parent_id, subchild.getId()) for subchild in child]

            # write id into idbase token_tree
            self.c.executemany("INSERT INTO token_tree VALUES(?,?, ?)", col_pair)
        self.conn.commit()

    def enterGraph(self, ctx):
        self.createNewTreeNodeWhileEntering()
        
    def exitGraph(self, ctx):
        self.addToDB(ctx, "graph")
        self.reassignCurrTreeNode()
        # for i in range(len(self.nodeProperties.elementList)):
        #    self.nodeProperties.elementList[i].printNode()

        # remove duplicates in the dictionary

        # find the most common element
        # naively using the first one

    # Enter a parse tree produced by DOTParser#stmt_list.
    def enterStmt_list(self, ctx:DOTParser.Stmt_listContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#stmt_list.
    def exitStmt_list(self, ctx:DOTParser.Stmt_listContext):
        self.addToDB(ctx, "stmt_list")
        self.reassignCurrTreeNode()


    # Enter a parse tree produced by DOTParser#stmt.
    def enterStmt(self, ctx:DOTParser.StmtContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#stmt.
    def exitStmt(self, ctx:DOTParser.StmtContext):
        self.addToDB(ctx, "stmt")
        self.reassignCurrTreeNode()


    # Enter a parse tree produced by DOTParser#attr_stmt.
    def enterAttr_stmt(self, ctx:DOTParser.Attr_stmtContext):
        
        # change CeurrAttrType
        if ctx.GRAPH() is not None:
            self.currAttrType = 0
        elif ctx.NODE() is not None:
            self.currAttrType = 1
        elif ctx.EDGE() is not None:
            self.currAttrType = 2
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#attr_stmt.
    def exitAttr_stmt(self, ctx:DOTParser.Attr_stmtContext):
        self.addToDB(ctx, "attr_stmt")
        self.reassignCurrTreeNode()
        self.currAttrType = 0

    # Enter a parse tree produced by DOTParser#attr_list.
    def enterAttr_list(self, ctx:DOTParser.Attr_listContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#attr_list.
    def exitAttr_list(self, ctx:DOTParser.Attr_listContext):
        self.addToDB(ctx, "attr_list")
        self.reassignCurrTreeNode()


    # Enter a parse tree produced by DOTParser#a_list.
    def enterA_list(self, ctx:DOTParser.A_listContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#a_list.
    def exitA_list(self, ctx:DOTParser.A_listContext):
        self.addToDB(ctx, "a_list")
        self.reassignCurrTreeNode()

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
        self.createNewTreeNodeWhileEntering()
        self.edgeProperties.addNewEdge()
        self.currAttrType = 2

    # Exit a parse tree produced by DOTParser#edge_stmt.
    def exitEdge_stmt(self, ctx:DOTParser.Edge_stmtContext):
        self.addToDB(ctx, "edge_stmt")
        self.reassignCurrTreeNode()
        self.edgeProperties.flushNewEdge()
        self.currAttrType = 0


    # Enter a parse tree produced by DOTParser#edgeRHS.
    def enterEdgeRHS(self, ctx:DOTParser.EdgeRHSContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#edgeRHS.
    def exitEdgeRHS(self, ctx:DOTParser.EdgeRHSContext):
        self.addToDB(ctx, "edge_RHS")
        self.reassignCurrTreeNode()

    # Enter a parse tree produced by DOTParser#edgeop.
    def enterEdgeop(self, ctx:DOTParser.EdgeopContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#edgeop.
    def exitEdgeop(self, ctx:DOTParser.EdgeopContext):
        self.addToDB(ctx, "edge_op")
        self.reassignCurrTreeNode()

    # Enter a parse tree produced by DOTParser#Node_stmt.
    def enterNode_stmt(self, ctx:DOTParser.Node_stmtContext):
        self.createNewTreeNodeWhileEntering()
        self.nodeProperties.addNewNode()
        self.currAttrType = 1

    # Exit a parse tree produced by DOTParser#Node_stmt.
    def exitNode_stmt(self, ctx:DOTParser.Node_stmtContext):
        self.addToDB(ctx, "Node_stmt")
        self.reassignCurrTreeNode()
        self.nodeProperties.flushNewNode()
        self.currAttrType = 0

    # Enter a parse tree produced by DOTParser#Node_id.
    def enterNode_id(self, ctx:DOTParser.Node_idContext):
        self.createNewTreeNodeWhileEntering()
        if self.nodeProperties.getIsTempAttr() == 1:
            self.nodeProperties.setCurrNodeName(ctx.getText())
        elif self.edgeProperties.getIsTempAttr() == 1:
            self.edgeProperties.setCurrLeftNodeName(ctx.getText())
            self.edgeProperties.setIsTempAttr(2);
        elif self.edgeProperties.getIsTempAttr() == 2:
            self.edgeProperties.setCurrRightNodeName(ctx.getText())

    # Exit a parse tree produced by DOTParser#Node_id.
    def exitNode_id(self, ctx:DOTParser.Node_idContext):
        self.addToDB(ctx, "Node_id")
        self.reassignCurrTreeNode()


    # Enter a parse tree produced by DOTParser#port.
    def enterPort(self, ctx:DOTParser.PortContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#port.
    def exitPort(self, ctx:DOTParser.PortContext):
        self.addToDB(ctx, "port")
        self.reassignCurrTreeNode()


    # Enter a parse tree produced by DOTParser#subgraph.
    def enterSubgraph(self, ctx:DOTParser.SubgraphContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#subgraph.
    def exitSubgraph(self, ctx:DOTParser.SubgraphContext):
        self.addToDB(ctx, "subgraph")
        self.reassignCurrTreeNode()


    # Enter a parse tree produced by DOTParser#id_decl.
    def enterId_decl(self, ctx:DOTParser.Id_declContext):
        self.createNewTreeNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#id_decl.
    def exitId_decl(self, ctx:DOTParser.Id_declContext):
        self.addToDB(ctx, "id")
        self.reassignCurrTreeNode()


    def __del__(self):
        self.conn.close()

def main():
    input_file = args.infile
    if args.outfile is None:
        output_file = input_file.split(".")[0] + ".db"
    else:
        output_file = args.outfile
    # parse dot/gv file and build idbase
    input_stream = FileStream(input_file)
    lexer = DOTLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DOTParser(stream)
    tree = parser.graph()
    printer = DOTPrintListener(output_file)
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

    propertyList = printer.getNodeProperties().getElementList()
    if args.fca:
        # fca
        fca = FCA(propertyList)
        fca.createNodesGraphviz( input_file.split(".")[0] + "_nodes.dot")

    # powerset formation
    createTypeHierachyGraph(propertyList)

def createTypeHierachyGraph(propertyList):
    # powerset construction
    commonKeys, structuredDict = preprocessing(propertyList)
    # outputJson(structuredDict)

    # typeHierachy = TypeHierachy(structuredDict)

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
    parser.add_argument('-outfile', 
                        help='name of the output idbase file')
    parser.add_argument('infile', 
                        help='name of the input dot/gv file')
    parser.add_argument('-fca', action='store_true')

    args = parser.parse_args()
    main()
