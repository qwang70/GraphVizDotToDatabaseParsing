import sqlite3
from antlr4.tree.Tree import TerminalNodeImpl 
from antlr4 import *
from DOTLexer import DOTLexer
from DOTListener import DOTListener
from DOTParser import DOTParser
import sys
import argparse

class Node(object):
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
        self.numToken = 0
        self.copyTree = None
        self.currNode = None

        self.conn = sqlite3.connect(output_file)
        self.c = self.conn.cursor()
        # create tokens table
        self.c.execute("DROP TABLE IF EXISTS tokens")
        self.c.execute("CREATE TABLE tokens(Id integer primary key,token_type text, token_val  text)")

        # create table for searching parent and children
        self.c.execute("DROP TABLE IF EXISTS token_tree")
        self.c.execute("CREATE TABLE token_tree(Id integer,parent_id integer, child_id integer)")

    def createNewNodeWhileEntering(self):
        # initiate new node for self
        newNode = Node(self.numToken)
        if self.copyTree is None:
            self.copyTree = newNode
        else:
            newNode.setParent(self.currNode)
            self.currNode.add_child(newNode)
        self.currNode = newNode
        self.numToken += 1

    
    def reassignCurrNode(self):
        # assign the current node to be its parent node
        assert self.currNode is not None
        self.currNode = self.currNode.getParent()

    def addToDB(self, ctx, type_val):
        self.c.execute("INSERT INTO tokens VALUES(?, ?, ?)", (self.currNode.getId(), type_val, ctx.getText()))
        # assign parent id
        if self.currNode.getParent() is None: 
            parent_id = None
        else:
            parent_id = self.currNode.getParent().getId()
        # assign a list of child id
        if ctx.getChildCount() == 0:
            child = None
        else:
            child = []
            nodeChildIdx = 0
            for i in range(ctx.getChildCount()):
                # check whether the child is a terminal node
                #if type(ctx.getChild(i)) is antlr4.tree.Tree.TerminalNodeImpl:
                if type(ctx.getChild(i)) is TerminalNodeImpl:
                    terminalCtx = ctx.getChild(i)
                    #self.c.execute("INSERT INTO tokens VALUES(?,?, ?)", (self.numToken, "symbol", ctx.getText()))
                    self.c.execute("INSERT INTO tokens VALUES(?, ?, ?)", (self.numToken, "terminal", terminalCtx.getText()))
                    self.c.execute("INSERT INTO token_tree VALUES(?, ?, ?)", (self.numToken, self.currNode.id, None))
                    self.numToken += 1
                else:
                    assert nodeChildIdx < ctx.getChildCount()
                    child.append( self.currNode.getChild(nodeChildIdx) )
                    nodeChildIdx += 1
            if len(child) == 0:
                child = None
            # get all combinations of parent and child index
            if child is None:
                col_pair = [(self.currNode.getId(), parent_id, child)]
            else:
                col_pair = [(self.currNode.getId(), parent_id, subchild.getId()) for subchild in child]

            # write id into idbase token_tree
            self.c.executemany("INSERT INTO token_tree VALUES(?,?, ?)", col_pair)
        self.conn.commit()

    def enterGraph(self, ctx):
        self.createNewNodeWhileEntering()
        
        # ['DIGRAPH', 'EMPTY', 'GRAPH', 'STRICT', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'accept', 'addChild', 'addErrorNode', 'addTokenNode', 'children', 'copyFrom', 'depth', 'enterRule', 'exception', 'exitRule', 'getAltNumber', 'getChild', 'getChildCount', 'getChildren', 'getPayload', 'getRuleContext', 'getRuleIndex', 'getSourceInterval', 'getText', 'getToken', 'getTokens', 'getTypedRuleContext', 'getTypedRuleContexts', 'id_decl', 'invokingState', 'isEmpty', 'parentCtx', 'parser', 'removeLastChild', 'setAltNumber', 'start', 'stmt_list', 'stop', 'toString', 'toStringTree']
    def exitGraph(self, ctx):
        self.addToDB(ctx, "graph")
        self.reassignCurrNode()

    # Enter a parse tree produced by DOTParser#stmt_list.
    def enterStmt_list(self, ctx:DOTParser.Stmt_listContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#stmt_list.
    def exitStmt_list(self, ctx:DOTParser.Stmt_listContext):
        self.addToDB(ctx, "stmt_list")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#stmt.
    def enterStmt(self, ctx:DOTParser.StmtContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#stmt.
    def exitStmt(self, ctx:DOTParser.StmtContext):
        self.addToDB(ctx, "stmt")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#attr_stmt.
    def enterAttr_stmt(self, ctx:DOTParser.Attr_stmtContext):
        
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#attr_stmt.
    def exitAttr_stmt(self, ctx:DOTParser.Attr_stmtContext):
        self.addToDB(ctx, "attr_stmt")
        self.reassignCurrNode()

    # Enter a parse tree produced by DOTParser#attr_list.
    def enterAttr_list(self, ctx:DOTParser.Attr_listContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#attr_list.
    def exitAttr_list(self, ctx:DOTParser.Attr_listContext):
        self.addToDB(ctx, "attr_list")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#a_list.
    def enterA_list(self, ctx:DOTParser.A_listContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#a_list.
    def exitA_list(self, ctx:DOTParser.A_listContext):
        self.addToDB(ctx, "a_list")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#edge_stmt.
    def enterEdge_stmt(self, ctx:DOTParser.Edge_stmtContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#edge_stmt.
    def exitEdge_stmt(self, ctx:DOTParser.Edge_stmtContext):
        self.addToDB(ctx, "edge_stmt")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#edgeRHS.
    def enterEdgeRHS(self, ctx:DOTParser.EdgeRHSContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#edgeRHS.
    def exitEdgeRHS(self, ctx:DOTParser.EdgeRHSContext):
        self.addToDB(ctx, "edge_RHS")
        self.reassignCurrNode()

    # Enter a parse tree produced by DOTParser#edgeop.
    def enterEdgeop(self, ctx:DOTParser.EdgeopContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#edgeop.
    def exitEdgeop(self, ctx:DOTParser.EdgeopContext):
        self.addToDB(ctx, "edge_op")
        self.reassignCurrNode()

    # Enter a parse tree produced by DOTParser#node_stmt.
    def enterNode_stmt(self, ctx:DOTParser.Node_stmtContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#node_stmt.
    def exitNode_stmt(self, ctx:DOTParser.Node_stmtContext):
        self.addToDB(ctx, "node_stmt")
        self.reassignCurrNode()

    # Enter a parse tree produced by DOTParser#node_id.
    def enterNode_id(self, ctx:DOTParser.Node_idContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#node_id.
    def exitNode_id(self, ctx:DOTParser.Node_idContext):
        self.addToDB(ctx, "node_id")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#port.
    def enterPort(self, ctx:DOTParser.PortContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#port.
    def exitPort(self, ctx:DOTParser.PortContext):
        self.addToDB(ctx, "port")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#subgraph.
    def enterSubgraph(self, ctx:DOTParser.SubgraphContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#subgraph.
    def exitSubgraph(self, ctx:DOTParser.SubgraphContext):
        self.addToDB(ctx, "subgraph")
        self.reassignCurrNode()


    # Enter a parse tree produced by DOTParser#id_decl.
    def enterId_decl(self, ctx:DOTParser.Id_declContext):
        self.createNewNodeWhileEntering()

    # Exit a parse tree produced by DOTParser#id_decl.
    def exitId_decl(self, ctx:DOTParser.Id_declContext):
        self.addToDB(ctx, "id")
        self.reassignCurrNode()


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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A GraphViz dot file to Sqlite idbase converter.')
    parser.add_argument('-outfile', 
                        help='name of the output idbase file')
    parser.add_argument('infile', 
                        help='name of the input dot/gv file')

    args = parser.parse_args()
    main()
