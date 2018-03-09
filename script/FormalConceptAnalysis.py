from concepts import Context
import pandas as pd
import numpy as np
from fcaVisualize import *

def graphviz(self, filename=None, directory=None, render=False, view=False, **kwargs):
    """Return graphviz source for visualizing the lattice graph."""
    return lattice(self, filename, directory, render, view, **kwargs)

class FCA(object):
    def __init__(self, propertyList):
        # get objs and attrs
        index = [elem.get_name() for elem in propertyList]
        attrs = set()
        for elem in propertyList:
            currAttr = elem.getAttr() 
            for key, val in currAttr.items():
                if key.lower() != "label" and \
                    "{}={}".format(key,val) not in attrs:
                    attrs.add("{}={}".format(key,val))
        # create FCA
        self.fca = pd.DataFrame(index=index, columns=attrs)
        self.fca = self.fca.fillna("") # with 0s rather than NaNs
        for elem in propertyList:
            currAttr = elem.getAttr() 
            label = None
            for key, val in currAttr.items():
                if key.lower() != "label":
                    self.fca.loc[[elem.get_name()], "{}={}".format(key,val)] = "X"
                elif val != "\"\"" and val != "\'\'":
                    label = val
            if label is not None:
                self.fca = self.fca.rename(index={elem.get_name(): label})
        ctx_string = self.fca.to_csv()
        self.ctx = Context.fromstring(ctx_string,frmat='csv')

    def createHierachyGraphviz(self, filename):
        dot = graphviz(self.ctx.lattice)
        dot.render(filename)

    def createNodesGraphviz(self, filename):
        nodesdot = ""
        atoms = self.ctx.lattice.atoms
        nid = 0
        """
        for nid, atom in enumerate(atoms):
            nodesdot += "n{} [{}, label=\"{}\"]\n".format(\
                    nid, ", ".join(atom.intent),\
                    "\\n".join(atom.extent).replace('\"', '\\\"') )
        """
        for atom in atoms:
            primaryNodeId = nid
            nodesdot += "n{} [{}, label=\"\"];\n".format(\
                    nid, ", ".join(atom.intent))
            nid += 1
            for nodeLabel in atom.extent:
                nodesdot += "n{} [{}, label={}];\n".format(\
                        nid, ", ".join(atom.intent), nodeLabel)
                nodesdot += "n{} -- n{};\n".format(primaryNodeId, nid)
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
            




